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

    # Model architecture
    vocab_size: int = 32000
    d_model: int = 256
    n_heads: int = 8
    n_layers: int = 4

    # Training hyperparameters
    batch_size: int = 32
    seq_len: int = 128
    lr: float = 1e-4
    max_steps: Optional[int] = None

    # === NEW: PyTorch Transformer optimization control ===
    enable_nested_tensor: bool = False

    # Checkpointing (SaveGame aware)
    checkpoint_dir: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "Saved" / "Checkpoints"
        )
    )
    checkpoint_interval: int = 200
    save_on_stable_loss: float = 2.5

    # Shared memory bridge to UE5
    telemetry_shm_name: str = "VersaiTelemetry"
    telemetry_size_mb: int = 128

    # Player data (future-proofing)
    data_source: str = "dummy"
    data_path: Optional[Path] = None

    # Ambience metadata (embedded in GGUF)
    metadata: dict = field(
        default_factory=lambda: {
            "versai_version": "1.0",
            "created_by": "Dave",
            "training_style": "self_supervised",
            "universe_seed": 42,
        }
    )

    @property
    def model_name(self) -> str:
        return f"versai_{self.style}_{self.d_model}M"

    def get_checkpoint_path(self, step: int) -> Path:
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return self.checkpoint_dir / f"{self.model_name}_step_{step:06d}.gguf"

    def to_dict(self) -> dict:
        return {
            "style": self.style,
            "d_model": self.d_model,
            "checkpoint_dir": str(self.checkpoint_dir),
            "metadata": self.metadata,
            "enable_nested_tensor": self.enable_nested_tensor,
        }


# Global default config
DEFAULT_CONFIG = TrainingConfig()
