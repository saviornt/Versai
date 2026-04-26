import multiprocessing.shared_memory as shm
import numpy as np
import pickle
import time
from typing import Optional

from .config import TrainingConfig


class VersaiSharedBuffer:
    """Zero-copy shared memory bridge between Python training core and UE5 Niagara NDI.

    This is the critical real-time telemetry pipe. UE5's C++ NDI will map the same
    named shared memory region and read the latest metrics every frame.
    """

    def __init__(self, config: Optional[TrainingConfig] = None):
        if config is None:
            from .config import DEFAULT_CONFIG

            config = DEFAULT_CONFIG

        self.name = config.telemetry_shm_name
        self.size = config.telemetry_size_mb * 1024 * 1024

        # Create or attach to the shared memory block
        try:
            self.shm = shm.SharedMemory(name=self.name, create=True, size=self.size)
            print(
                f"✅ Created new shared memory block: {self.name} ({self.size // 1024 // 1024} MB)"
            )
        except FileExistsError:
            self.shm = shm.SharedMemory(name=self.name, create=False)
            print(f"✅ Attached to existing shared memory block: {self.name}")

        # Numpy view over the raw buffer (zero-copy)
        self.buffer = np.ndarray((self.size,), dtype=np.uint8, buffer=self.shm.buf)
        self.offset = 0  # simple ring-buffer pointer for MVP

    def write_telemetry(
        self, loss: float, embeddings_norm: float, attention_max: float
    ):
        """Called every training step (or from FlexAttention telemetry_mod).

        Serializes a small dict and writes it to shared memory for UE5 to read.
        """
        data = {
            "loss": float(loss),
            "embed_norm": float(embeddings_norm),
            "attention_max": float(attention_max),
            "timestamp": time.time(),
            "style": "self_supervised",  # will become dynamic later
        }

        payload = pickle.dumps(data)
        header = len(payload).to_bytes(4, "little")  # 4-byte length prefix

        # Write header + payload (wrap around if needed)
        start = self.offset
        total_bytes = 4 + len(payload)

        if start + total_bytes > self.size:
            self.offset = 0  # wrap to beginning
            start = 0

        self.buffer[start : start + 4] = np.frombuffer(header, dtype=np.uint8)
        self.buffer[start + 4 : start + 4 + len(payload)] = np.frombuffer(
            payload, dtype=np.uint8
        )

        self.offset = (start + total_bytes) % self.size

    def close(self):
        """Clean shutdown — called in training.py finally block"""
        try:
            self.shm.close()
            self.shm.unlink()  # remove the named memory block
        except:
            pass
        print("🧹 Shared memory buffer closed")
