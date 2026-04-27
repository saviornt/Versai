from typing import Optional
from torch.utils.data import DataLoader

from .dataset import MultimodalDataset

from Versai.settings import settings


def get_dataloader(batch_size: Optional[int] = None):
    """Return a PyTorch DataLoader for the current data source."""
    if batch_size is None:
        batch_size = settings.batch_size

    dataset = MultimodalDataset()

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True,
        drop_last=True,
        persistent_workers=True,
    )
