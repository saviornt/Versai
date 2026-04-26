from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class TrainingConfig:
    """Central configuration for Versai training core.
    UE5 will be able to override any of these via shared memory later.
    """
    # Training style (MVP: self_supervised is fully implemented)
    style: str = "self_supervised"

    # Model architecture (kept small for real-time on RTX 3080)
    vocab_size: int = 32000
    d_model: int = 256
    n_heads: int = 8
    n_layers: int = 4

    # Training hyperparameters
    batch_size: int = 32
    seq_len: int = 128
    lr: float = 1e-4
    max_steps: Optional[int] = None          # None = run forever until user stops

    # Checkpointing (SaveGame aware)
    checkpoint_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "Saved" / "Checkpoints"
    )
    checkpoint_interval: int = 200           # steps between auto-saves
    save_on_stable_loss: float = 2.5         # save when loss drops below this

    # Shared memory bridge to UE5
    telemetry_shm_name: str = "VersaiTelemetry"
    telemetry_size_mb: int = 128

    # Player data (future-proofing for data upload)
    data_source: str = "dummy"               # "dummy", "file", "player_upload"
    data_path: Optional[Path] = None

    # Ambience metadata (embedded in GGUF)
    metadata: dict = field(default_factory=lambda: {
        "versai_version": "1.0",
        "created_by": "Dave",
        "training_style": "self_supervised",
        "universe_seed": 42
    })

    @property
    def model_name(self) -> str:
        return f"versai_{self.style}_{self.d_model}M"

    def get_checkpoint_path(self, step: int) -> Path:
        """Returns full path for GGUF file"""
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return self.checkpoint_dir / f"{self.model_name}_step_{step:06d}.gguf"

    def to_dict(self) -> dict:
        """For easy serialization to shared memory / UE5"""
        return {
            "style": self.style,
            "d_model": self.d_model,
            "checkpoint_dir": str(self.checkpoint_dir),
            "metadata": self.metadata
        }

# Global default config (can be overridden by UE5 HUD later)
DEFAULT_CONFIG = TrainingConfig()