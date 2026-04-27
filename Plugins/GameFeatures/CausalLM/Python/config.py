from pydantic_settings import BaseSettings, SettingsConfigDict


class CausalLMConfig(BaseSettings):
    """CausalLM-specific configuration — fully driven by environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="VERSAI_CAUSALLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model architecture
    vocab_size: int = 32000
    d_model: int = 256
    n_heads: int = 8
    n_layers: int = 4
    feedforward_multiplier: int = 4

    # Training hyperparameters
    batch_size: int = 32
    seq_length: int = 128

    # Additional training parameters
    learning_rate: float = 0.0001
    dropout: float = 0.1
    activation_function: str = "gelu"
    batch_first: bool = True
    norm_first: bool = True
    bias: bool = True
