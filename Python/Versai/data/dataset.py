from torch.utils.data import Dataset
from typing import Dict, Any
import json

from Versai.settings import settings


class MultimodalDataset(Dataset):
    """Generic multimodal dataset that supports single-type or multimodal data."""

    def __init__(self):
        self.data_source = settings.data_source
        self.data_path = settings.data_path

        if self.data_source == "dummy":
            self.data = list(range(10000))  # dummy for testing
        elif self.data_path and self.data_path.exists():
            # Basic support for text/JSON for MVP
            if self.data_path.suffix == ".json":
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.data = f.readlines()
        else:
            self.data = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.data[idx]
        return {
            "text": item if isinstance(item, str) else str(item),
            "raw": item,
            "index": idx,
        }
