# Python Playground API

**Versai – Procedural Vibe Training Simulator**  
**Document Version:** 1.0 (April 27, 2026)  
**Status:** Active – Single source of truth for the Python backend  
**File Location:** `docs/Python_Playground_API.md`  
**References:** `Python/Versai/core.py`, `settings.py`, `shared_memory.py`, `gguf_fileops.py`, `SharedMemory_StructuredBuffer_Design.md`, Architecture Design Document v3

---

## 1. Current Direction (Live Implementation)

The Playground is the **Python/Versai** package that owns:

* Training loop (PyTorch 2.11 transformer + FlexAttention telemetry)
* Data loading / reduction layer
* GGUF checkpointing
* Shared-memory bridge to UE5 (NiagaraDataInterface → PCG + Niagara hybrid)

**Core entry point:** `core.py`

```python
# Python/Versai/core.py (live)
def main():
    # ... argparse + branch logic
    run_training = load_plugin_trainer(plugin_name)  # dynamic import from Plugins/GameFeatures/<plugin>/Python/<plugin>.trainer
    telemetry = VersaiSharedBuffer()                 # current pickle-based buffer
    run_training(telemetry_buffer=telemetry, ...)
```

**Key characteristics (as of commit 53e9f0d)**:

* Plugin-driven modularity via `importlib` + `sys.path` injection (Game Feature Plugins provide the actual `trainer` module).
* Settings fully driven by `VERSAI_` environment variables (Pydantic v2).
* Basic scalar telemetry via `VersaiSharedBuffer` (circular `uint8` + `pickle`).
* GGUF auto-save via `gguf_fileops.py`.
* GIL-locked Python 3.14 safe (training runs in separate process).

**Strengths**: Already supports hot-swap of training styles via plugins and branch management.  
**Limitations**: Legacy shared-memory (pickle + single buffer) blocks full PCG/Niagara performance.

---

## 2. MVP (Next Sprint – Phase 1)

**Goal**: Make the Playground production-ready for the hybrid NDI → PCG + Niagara architecture while preserving the existing plugin system.

**Required deliverables**:

1. **Add `VersaiStructuredBuffer`** (see `SharedMemory_StructuredBuffer_Design.md`).
2. **Create `core/schemas.py`** with Pydantic models + NumPy structured dtypes.
3. **Implement data-reduction layer** in each plugin’s `trainer.py`:

   ```python
   def reduce_model_state(model, step: int) -> LayerFrame:
       """Transform raw tensors → GPU-friendly PCG structs (zero allocation)."""
       # ... feature extraction
       return LayerFrame(...)  # Pydantic model
   ```

4. **Update `core.py` training orchestration**:

   ```python
   # New in main()
   structured_buffer = VersaiStructuredBuffer()
   run_training(telemetry_buffer=structured_buffer, ...)  # pass structured buffer
   ```

5. **Keep `VersaiSharedBuffer` side-by-side** for scalar fallback during transition.
6. **Expose clean API** for plugins (no direct shared-memory knowledge).

**MVP success criteria**:

* Training loop writes reduced `LayerFrame` to double-buffered structured memory.
* UE5 NDI can read latest frame and feed PCG + Niagara with zero-copy.
* All code follows: Pydantic v2, Google-style docstrings, async-first where possible, strict typing, no emojis.

---

## 3. Optimization (Post-MVP – Phase 2)

Focus on **performance gains** when paired with UE5 shared-memory + RTX 3080 (or older hardware) and GIL-locked Python 3.14:

| Area                        | Current | Optimized Target                              | Expected Gain |
|-----------------------------|---------|-----------------------------------------------|---------------|
| Shared-memory write         | pickle + circular | Structured NumPy views + double buffering    | < 0.8 ms/frame |
| Reduction layer             | ad-hoc     | Vectorized NumPy + pre-allocated arrays       | 3-5× faster |
| Training process isolation  | basic      | Dedicated `multiprocessing.Process` + sub-interpreter | No GIL contention for audio/NDI |
| Data transfer to UE5        | scalar only| Zero-copy reinterpret in C++ NDI              | < 0.4 ms read |
| Hot-reload / plugin swap    | full restart | Live plugin re-import + buffer recreation only| Instant style switch |

**Techniques to apply**:

* Use `np.ndarray(..., buffer=shm.buf, dtype=NEURON_DTYPE)` everywhere.
* `asyncio` + threading for non-blocking reduction (Python 3.14 free-threaded prep).
* Cache-aligned structs (`alignas(64)`) on C++ side.
* Minimal per-frame data (only changed neurons/connections via diffing).
* Torch `compile` + FlexAttention `score_mod` telemetry hooks (already in settings).

**Target**: 60 FPS UE5 frame rate with training loop at full speed on RTX 3080-class hardware.

---

## 4. Future Enhancements (Phase 3+ / Post-MVP)

* **Python 3.15 migration** – Leverage improved allocator + JIT for 15-25 % overall speedup.
* **Full free-threaded build** – Remove GIL entirely for audio + sonification sub-interpreters.
* **Plugin hot-reload without restart** – `importlib.reload` + buffer state migration.
* **Multi-model / universe merging** – Shared buffer supports multiple `LayerFrame` streams.
* **Deterministic replay mode** – Record shared-memory snapshots for training playback.
* **Bio-reactive inputs** – Real-time sensor streams injected into reduction layer.
* **GGUF + Ambience Metadata embedding** – Extend `gguf_fileops.py` to store PCG/Niagara presets.
* **Distributed Playground (stretch)** – Optional Ray / Dask for larger models while keeping single-player local mode.

**All enhancements will maintain**:

* Backward compatibility with existing plugins.
* Zero dynamic allocation in hot path.
* Strict adherence to Pydantic v2 settings pattern (`VERSAI_*` → `settings.*`).

---

**This document is a living blueprint.**  
It will be updated at the end of every sprint. All tasks above are written as ready-to-drop Kanban cards.
