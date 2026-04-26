import gguf
import torch
from pathlib import Path
from typing import Optional

from .config import TrainingConfig


def save_to_gguf(
    model: torch.nn.Module,
    config: TrainingConfig,
    step: int,
    custom_metadata: Optional[dict] = None,
):
    """Export the current model state as a proper GGUF file with embedded Ambience Metadata."""
    # Ensure checkpoint directory exists (Saved/Checkpoints/)
    config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    filepath = config.get_checkpoint_path(step)

    # Initialize GGUF writer (Llama architecture = maximum compatibility)
    writer = gguf.GGUFWriter(str(filepath), "llama")

    # === Save all model weights ===
    state_dict = model.state_dict()
    for name, param in state_dict.items():
        tensor = param.detach().cpu().numpy()
        writer.add_tensor(name, tensor)

    # === Embed Versai "Ambience Metadata" ===
    metadata = {
        "versai.version": "1.0",
        "versai.style": config.style,
        "versai.step": step,
        "versai.d_model": config.d_model,
        "versai.n_heads": config.n_heads,
        "versai.n_layers": config.n_layers,
        "versai.vocab_size": config.vocab_size,
        "versai.created_by": "Dave",
        "versai.training_date": str(config.checkpoint_dir),
        **(custom_metadata or {}),
    }

    for key, value in metadata.items():
        if isinstance(value, str):
            vtype = gguf.GGUFValueType.STRING
        elif isinstance(value, int):
            vtype = gguf.GGUFValueType.INT32
        elif isinstance(value, float):
            vtype = gguf.GGUFValueType.FLOAT32
        else:
            vtype = gguf.GGUFValueType.STRING
        writer.add_key_value(key, value, vtype)

    # === Write everything to disk (correct 2026 API) ===
    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    writer.write_tensors_to_file()  # ← This is the correct high-level call
    writer.close()

    print(f"✅ GGUF checkpoint saved → {filepath.name}")
    print(
        f"   Style: {config.style} | Step: {step} | Size: {filepath.stat().st_size / 1024 / 1024:.1f} MB"
    )
    return filepath


# Quick test helper (run this file directly to verify)
if __name__ == "__main__":
    from .config import DEFAULT_CONFIG

    print("🧪 Testing GGUF exporter with dummy model...")

    class DummyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.embed = torch.nn.Embedding(32000, 256)

    dummy = DummyModel()
    save_to_gguf(dummy, DEFAULT_CONFIG, step=0)
