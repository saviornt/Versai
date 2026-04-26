from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class VersaiSettings(BaseSettings):
    """Main Versai settings — fully driven by environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="VERSAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    training_style: str = "self_supervised"

    # Global defaults (can be overridden per-plugin via env vars)
    vocab_size: int = 32000
    d_model: int = 256
    n_heads: int = 8
    n_layers: int = 4
    feedforward_multiplier: int = 4

    batch_size: int = 32
    seq_len: int = 128
    lr: float = 0.0001
    dropout: float = 0.1
    activation_function: str = "gelu"

    batch_first: bool = True
    norm_first: bool = True
    bias: bool = True

    checkpoint_interval: int = 200
    save_on_stable_loss: float = 2.5

    telemetry_shm_name: str = "VersaiTelemetry"
    telemetry_size_mb: int = 128

    enable_torch_compile: bool = False

    active_plugin: Optional[str] = None
    plugin_path: Optional[Path] = None

    checkpoint_dir: Path = Path(__file__).parent.parent.parent / "Saved" / "Checkpoints"


# Global instance
settings = VersaiSettings()
