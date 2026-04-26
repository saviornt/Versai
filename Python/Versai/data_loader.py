import torch
from .config import TrainingConfig


def get_dummy_batch(config: TrainingConfig, device: str) -> torch.Tensor:
    """MVP data loader — returns a simple random batch for causal LM.
    Later this will be replaced by player-uploaded data (text, protein sequences, etc.)
    with proper tokenization and streaming.
    """
    return torch.randint(
        0,
        config.vocab_size,
        (config.batch_size, config.seq_len),
        device=device,
        dtype=torch.long,
    )
