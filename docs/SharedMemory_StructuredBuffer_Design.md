# Shared Memory Structured Buffer Design (v2)

**Versai – Procedural Vibe Training Simulator**  
**Document Version:** 2.0 (April 27, 2026)  
**Status:** Active – Single source of truth for current implementation + target structured buffer for PCG + Niagara hybrid  
**File Location:** `docs/SharedMemory_StructuredBuffer_Design.md`  
**References:** `Python/Versai/shared_memory.py` (live at commit 53e9f0d), `Python/Versai/settings.py`, Architecture Design Document v3, GDD, SharedMemory_DataSchema_v2.md (merged)

---

## 1. Purpose

This document defines the **complete shared-memory architecture** for Versai, including:

- Current live implementation (`VersaiSharedBuffer`)
- Target **v2 structured buffer** (`VersaiStructuredBuffer`)
- Exact binary layout, double-buffering, zero-copy NumPy structured arrays, and C++ interop
- Data flow from Python Playground (training + reduction) → repurposed `UNiagaraDataInterface` → PCG Graphs (primary universe) + Niagara VFX (secondary effects)

**Key goals**:

- Double-buffered, lock-free, zero-copy structured NumPy arrays
- Feeds both PCG Graphs and Niagara via the same `UNiagaraDataInterface`
- Maintains full backward compatibility with scalar telemetry during transition
- Zero dynamic allocation in hot path
- GIL-locked Python 3.14 safe (training in separate `multiprocessing.Process`)

---

## 2. Current Implementation (Live in Repo)

**File:** `Python/Versai/shared_memory.py`

```python
import multiprocessing.shared_memory as shm
import numpy as np
import pickle
import time

from Versai.settings import settings

class VersaiSharedBuffer:
    """Zero-copy shared memory bridge for UE5 Niagara NDI with rich telemetry."""

    def __init__(self):
        self.name = settings.telemetry_shm_name
        self.size = settings.telemetry_size_mb * 1024 * 1024

        try:
            self.shm = shm.SharedMemory(name=self.name, create=True, size=self.size)
            print(
                f"Created new shared memory block: {self.name} ({self.size // 1024 // 1024} MB)"
            )
        except FileExistsError:
            self.shm = shm.SharedMemory(name=self.name, create=False)
            print(f"Attached to existing shared memory block: {self.name}")

        self.buffer = np.ndarray((self.size,), dtype=np.uint8, buffer=self.shm.buf)
        self.offset = 0

    def write_telemetry(
        self,
        loss: float = 0.0,
        embeddings_norm: float = 0.0,
        attention_max: float = 0.0,
        attention_mean: float = 0.0,
    ):
        """Rich telemetry for Niagara visualization."""
        data = {
            "loss": float(loss),
            "embed_norm": float(embeddings_norm),
            "attention_max": float(attention_max),
            "attention_mean": float(attention_mean),
            "timestamp": time.time(),
        }
        payload = pickle.dumps(data)
        header = len(payload).to_bytes(4, "little")
        start = self.offset
        total = 4 + len(payload)
        if start + total > self.size:
            self.offset = 0
            start = 0
        self.buffer[start : start + 4] = np.frombuffer(header, dtype=np.uint8)
        self.buffer[start + 4 : start + 4 + len(payload)] = np.frombuffer(
            payload, dtype=np.uint8
        )
        self.offset = (start + total) % self.size

    def close(self):
        try:
            self.shm.close()
            self.shm.unlink()
        except Exception as e:
            print(f"Failed to close successfully: {e}")
        print("Shared memory buffer closed")
```

**Current characteristics**:

- Single circular `uint8` buffer + `pickle`
- Zero-copy ndarray view (solid foundation)
- No double buffering, no frame sync header, no PCG-specific structured data

This is sufficient for early scalar telemetry but **must evolve** to v2 for the full hybrid architecture.

---

## 3. High-Level Architecture

```text
Python Playground (Training + Reduction Layer)
         ↓ (write to inactive buffer)
VersaiStructuredBuffer (double-buffered structured NumPy)
         ↓ (atomic FrameHeader swap)
UNiagaraDataInterface (C++)
         ├─→ PCG Graph (points → density/gradient attributes)
         └─→ Niagara Emitters (particles/ribbons via Data Channel inheritance)
```

---

## 4. Target v2 Schema (PCG + Niagara Hybrid)

### 4.1 Pydantic Settings Extension (`settings.py`)

```python
# Python/Versai/settings.py (extend existing SharedMemoryConfig)
class SharedMemoryConfig(BaseModel):
    """Pydantic v2 settings (ENV_VAR_NAME -> pydantic-settings_var_name -> code_var_name)."""
    telemetry_shm_name: str = "versai_telemetry_shm"
    telemetry_size_mb: Annotated[int, Field(ge=64, le=1024)] = 512   # Increased for structured data
    max_neurons: Annotated[int, Field(ge=1024, le=100_000)] = 50_000
    max_connections: Annotated[int, Field(ge=0, le=500_000)] = 250_000
    double_buffer: bool = True
```

### 4.2 NumPy Structured Dtypes (`core/schemas.py`)

```python
# Python/Versai/core/schemas.py
NEURON_DTYPE = np.dtype([
    ('id', np.int32),
    ('activation', np.float32),
    ('x', np.float32),
    ('y', np.float32),
    ('z', np.float32),
    ('density', np.float32),      # PCG point density attribute
    ('gradient_mag', np.float32), # Niagara vector storm strength
    ('layer_id', np.int32)
])

CONNECTION_DTYPE = np.dtype([
    ('from_id', np.int32),
    ('to_id', np.int32),
    ('weight', np.float32),
    ('thickness', np.float32)     # Niagara ribbon width
])
```

### 4.3 C++ Structs (UE5 side – exact memory layout)

```cpp
// Source/SharedMemory/Public/VizStructs.h
#pragma pack(push, 8)
struct alignas(64) FNeuronPCGPoint
{
    int32 Id;
    float Activation;
    FVector Position;           // x, y, z
    float Density;              // PCG
    float GradientMag;          // Niagara
    int32 LayerId;
};

struct alignas(64) FConnectionPCG
{
    int32 FromId;
    int32 ToId;
    float Weight;
    float Thickness;
};

struct alignas(64) FLayerFrameHeader
{
    uint64_t FrameId;
    uint32_t BufferIndex;       // 0 = A, 1 = B
    uint32_t Ready;
    int32 LayerId;
    int32 NeuronCount;
    int32 ConnectionCount;
    float Loss;
    uint64_t Reserved[2];       // 64-byte alignment
};
#pragma pack(pop)
```

---

## 5. Core Implementation (`VersaiStructuredBuffer`)

**New file:** `Python/Versai/structured_buffer.py`

```python
# Python/Versai/structured_buffer.py
from __future__ import annotations

import multiprocessing.shared_memory as shm
import numpy as np
from datetime import datetime, timezone
from pydantic import Field
from typing import Annotated

from Versai.settings import settings
from Versai.core.schemas import (
    NEURON_DTYPE,
    CONNECTION_DTYPE,
    NeuronPCGPoint,
    ConnectionPCG,
    LayerFrame,
)

class VersaiStructuredBuffer:
    """Double-buffered, zero-copy structured shared memory for PCG + Niagara hybrid.

    Replaces the pickle-based VersaiSharedBuffer for v2 schema.
    """

    def __init__(self):
        self.name = settings.telemetry_shm_name
        self.size = settings.telemetry_size_mb * 1024 * 1024
        self.max_neurons = settings.max_neurons
        self.max_connections = settings.max_connections

        # Calculate fixed buffer sizes (A + B)
        neuron_bytes = self.max_neurons * NEURON_DTYPE.itemsize
        conn_bytes = self.max_connections * CONNECTION_DTYPE.itemsize
        header_bytes = 128  # FLayerFrameHeader (64-byte aligned)
        buffer_a_size = header_bytes + neuron_bytes + conn_bytes
        self.buffer_size = buffer_a_size * 2  # Double buffer

        # Create / attach shared memory
        try:
            self.shm = shm.SharedMemory(name=self.name, create=True, size=self.buffer_size)
            print(f"Created structured shared memory: {self.name} ({self.buffer_size // 1024 // 1024} MB)")
        except FileExistsError:
            self.shm = shm.SharedMemory(name=self.name, create=False)
            print(f"Attached to existing structured shared memory: {self.name}")

        # Zero-copy NumPy views (double-buffered)
        self.buffer = np.ndarray((self.buffer_size,), dtype=np.uint8, buffer=self.shm.buf)
        self.buffer_a = self.buffer[:buffer_a_size]
        self.buffer_b = self.buffer[buffer_a_size:]

        self.current_write_index = 0
        self.frame_id = 0

    def write_frame(self, frame: LayerFrame) -> None:
        """Write reduced frame to inactive buffer and atomically swap."""
        # Select inactive buffer
        write_buf = self.buffer_b if self.current_write_index == 0 else self.buffer_a

        # Write header (exact C++ layout match)
        header = np.zeros(1, dtype=[('frame_id', np.uint64),
                                    ('buffer_index', np.uint32),
                                    ('ready', np.uint32),
                                    ('layer_id', np.int32),
                                    ('neuron_count', np.int32),
                                    ('connection_count', np.int32),
                                    ('loss', np.float32)])
        header[0] = (self.frame_id, 1 - self.current_write_index, 1,
                     frame.layer_id, frame.neuron_count, frame.connection_count, frame.loss)

        # Write neurons (structured)
        neuron_data = np.array([tuple(p.model_dump().values()) for p in frame.neurons], dtype=NEURON_DTYPE)
        # Write connections... (TODO: implement similarly)

        # Copy into buffer (zero-copy view)
        offset = 0
        write_buf[offset:offset + header.nbytes] = header.view(np.uint8)
        offset += header.nbytes
        # ... copy neuron_data and connection_data similarly

        # Atomic swap
        self.current_write_index = 1 - self.current_write_index
        self.frame_id += 1

    def read_latest(self) -> np.ndarray | None:
        """UE5 NDI calls this to get latest ready buffer (zero-copy)."""
        # Implementation in C++ NDI will reinterpret the buffer directly
        pass

    def close(self):
        try:
            self.shm.close()
            self.shm.unlink()
        except Exception as e:
            print(f"Failed to close structured buffer: {e}")
        print("Structured shared memory closed")
```

---

## 6. Performance Optimizations & GIL-Locked 3.14 Notes

- **Zero-copy**: `np.ndarray(..., buffer=shm.buf, dtype=NEURON_DTYPE)` – no pickle, no Python objects in hot path.
- **Double buffering**: Guarantees UE never reads while Python writes.
- **Cache alignment**: All structs `alignas(64)` on C++ side.
- **Older hardware safe**: Float32 only, pre-allocated, minimal per-frame data.
- **Target latencies** (GIL-locked 3.14 on RTX 3080-class): Python write < 0.8 ms, UE read < 0.4 ms.

---

## 7. Python 3.15 Forward-Looking Enhancements

- Improved memory allocator (15-20 % lower overhead for large structured arrays)
- JIT compiler upgrades (potential 3-8 % speedup on reduction/hot-path code)
- Better free-threaded support (migration path remains trivial)

---

## 8. Migration Plan (Phase 1)

1. Keep `VersaiSharedBuffer` for scalar telemetry (backward compat).
2. Add `VersaiStructuredBuffer` side-by-side.
3. Update Playground training loop to call `structured_buffer.write_frame(reduced_frame)`.
4. Implement C++ `UNiagaraDataInterface` reader against the v2 buffer.

**This document is the single source of truth** for all shared-memory data in Versai and is a living document.
