from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional, Annotated
from pydantic import Field


class VersaiSettings(BaseSettings):
    """Main Versai settings — fully driven by environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="VERSAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Plugin / Model / Branch selection
    active_plugin: str = "CausalLM"
    model_name: str = "causal_lm"
    branch_name: str = "main"  # will be auto-incremented by core.py if needed

    # Data loading
    data_source: str = (
        "dummy"  # "dummy", "text", "protein", "sensor", "multimodal", etc.
    )
    data_path: Optional[Path] = None  # Path to dataset file/folder (set via env or arg)

    # Model architecture
    vocab_size: int = 32000
    d_model: int = 256
    n_heads: int = 8
    n_layers: int = 4
    feedforward_multiplier: int = 4

    # Training hyperparameters
    batch_size: int = 32
    seq_len: int = 128
    lr: float = 0.0001
    dropout: float = 0.1
    activation_function: str = "gelu"

    batch_first: bool = True
    norm_first: bool = True
    bias: bool = True

    # Training control
    max_steps: Optional[int] = None
    checkpoint_every_steps: int = 200
    checkpoint_every_minutes: Optional[float] = None

    # Shared memory (v2 structured buffer - replaces pickle)
    telemetry_shm_name: str = "versai_telemetry_shm"
    telemetry_size_mb: Annotated[int, Field(ge=64, le=1024)] = 512
    max_neurons: Annotated[int, Field(ge=1024, le=100_000)] = 50_000
    max_connections: Annotated[int, Field(ge=0, le=500_000)] = 250_000
    double_buffer: bool = True

    enable_torch_compile: bool = False

    checkpoint_dir: Path = Path(__file__).parent.parent.parent / "Saved" / "Checkpoints"


settings = VersaiSettings()
