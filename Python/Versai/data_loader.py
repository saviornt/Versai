import torch

from Versai.settings import settings


def get_dummy_batch():
    return torch.randint(
        0,
        settings.vocab_size,
        (settings.batch_size, settings.seq_len),
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
