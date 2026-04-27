from __future__ import annotations

import multiprocessing.shared_memory as shm
import numpy as np
from typing import Optional
from datetime import datetime, timezone

from Versai.settings import settings
from Versai.schemas import (
    NEURON_DTYPE,
    CONNECTION_DTYPE,
    LayerFrame,
    NeuronPCGPoint,
    ConnectionPCG,
)


class VersaiStructuredBuffer:
    """Double-buffered, zero-copy structured shared memory for PCG + Niagara hybrid.

    This is the production replacement for the legacy pickle-based VersaiSharedBuffer.
    Exact memory layout matches the C++ FLayerFrameHeader / FNeuronPCGPoint structs.
    """

    def __init__(self):
        self.name: str = settings.telemetry_shm_name
        self.max_neurons: int = settings.max_neurons
        self.max_connections: int = settings.max_connections

        # Fixed buffer sizes (double-buffered)
        header_bytes: int = 128  # 64-byte aligned FLayerFrameHeader
        neuron_bytes: int = self.max_neurons * NEURON_DTYPE.itemsize
        conn_bytes: int = self.max_connections * CONNECTION_DTYPE.itemsize
        buffer_a_size: int = header_bytes + neuron_bytes + conn_bytes
        self.buffer_size: int = buffer_a_size * 2

        # Create or attach shared memory
        try:
            self.shm = shm.SharedMemory(
                name=self.name, create=True, size=self.buffer_size
            )
            print(
                f"Created structured shared memory: {self.name} ({self.buffer_size // (1024 * 1024)} MB)"
            )
        except FileExistsError:
            self.shm = shm.SharedMemory(name=self.name, create=False)
            print(f"Attached to existing structured shared memory: {self.name}")

        self.buffer = np.ndarray(
            (self.buffer_size,), dtype=np.uint8, buffer=self.shm.buf
        )
        self.buffer_a = self.buffer[:buffer_a_size]
        self.buffer_b = self.buffer[buffer_a_size:]

        self.current_write_index: int = 0
        self.frame_id: int = 0

    def write_telemetry(
        self,
        loss: float = 0.0,
        embeddings_norm: float = 0.0,
        attention_max: float = 0.0,
        attention_mean: float = 0.0,
    ) -> None:
        """Legacy compatibility method during transition (scalar fallback).

        Creates a minimal single-neuron frame so existing trainers continue to work.
        """
        # Minimal frame for scalar telemetry
        dummy_neuron = NeuronPCGPoint(
            id=0,
            activation=float(embeddings_norm),
            x=0.0,
            y=0.0,
            z=0.0,
            density=1.0,
            gradient_mag=float(loss),
            layer_id=0,
        )
        frame = LayerFrame(
            frame_id=self.frame_id,
            layer_id=0,
            neuron_count=1,
            connection_count=0,
            loss=loss,
            neurons=[dummy_neuron],
            connections=[],
        )
        self.write_frame(frame)

    def write_frame(self, frame: LayerFrame) -> None:
        """Write a full reduced LayerFrame to the inactive buffer and atomically swap."""
        write_buf = self.buffer_b if self.current_write_index == 0 else self.buffer_a

        # --- Header (exact C++ layout)
        header_dtype = np.dtype(
            [
                ("frame_id", np.uint64),
                ("buffer_index", np.uint32),
                ("ready", np.uint32),
                ("layer_id", np.int32),
                ("neuron_count", np.int32),
                ("connection_count", np.int32),
                ("loss", np.float32),
            ]
        )
        header = np.zeros(1, dtype=header_dtype)
        header[0] = (
            self.frame_id,
            1 - self.current_write_index,
            1,  # ready flag
            frame.layer_id,
            frame.neuron_count,
            frame.connection_count,
            frame.loss,
        )

        # --- Neurons
        neuron_data = (
            np.array(
                [tuple(p.model_dump().values()) for p in frame.neurons],
                dtype=NEURON_DTYPE,
            )
            if frame.neurons
            else np.empty(0, dtype=NEURON_DTYPE)
        )

        # --- Connections
        conn_data = (
            np.array(
                [tuple(c.model_dump().values()) for c in frame.connections],
                dtype=CONNECTION_DTYPE,
            )
            if frame.connections
            else np.empty(0, dtype=CONNECTION_DTYPE)
        )

        # Zero-copy write
        offset = 0
        write_buf[offset : offset + header.nbytes] = header.view(np.uint8)
        offset += header.nbytes

        nbytes = len(neuron_data) * NEURON_DTYPE.itemsize
        if nbytes > 0:
            write_buf[offset : offset + nbytes] = neuron_data.view(np.uint8)
            offset += nbytes

        nbytes = len(conn_data) * CONNECTION_DTYPE.itemsize
        if nbytes > 0:
            write_buf[offset : offset + nbytes] = conn_data.view(np.uint8)

        # Atomic swap
        self.current_write_index = 1 - self.current_write_index
        self.frame_id += 1

    def close(self):
        """Clean shutdown."""
        try:
            self.shm.close()
            self.shm.unlink()
        except Exception as e:
            print(f"Failed to close structured buffer: {e}")
        print("Structured shared memory closed")
