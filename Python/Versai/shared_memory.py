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
                f"✅ Created new shared memory block: {self.name} ({self.size // 1024 // 1024} MB)"
            )
        except FileExistsError:
            self.shm = shm.SharedMemory(name=self.name, create=False)
            print(f"✅ Attached to existing shared memory block: {self.name}")

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
        print("🧹 Shared memory buffer closed")
