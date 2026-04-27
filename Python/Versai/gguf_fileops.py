import gguf
import torch
from pathlib import Path
from typing import Optional, Dict, Any

from Versai.settings import settings


def _get_branch_folder(model_name: str, branch_name: str) -> Path:
    """Return the correct branch folder, auto-incrementing if main already exists."""
    base = settings.checkpoint_dir / model_name

    if branch_name != "main":
        return base / branch_name

    # Auto-increment logic when branch_name is "main"
    main_folder = base / "main"
    if not main_folder.exists():
        return main_folder

    # Find next available branch-N
    i = 1
    while True:
        candidate = base / f"branch-{i}"
        if not candidate.exists():
            return candidate
        i += 1


def save_to_gguf(
    model: torch.nn.Module,
    step: int,
    branch_name: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
):
    """Save model to GGUF using the branch_name provided by the core."""
    if branch_name is None:
        branch_name = settings.branch_name

    # Dynamic folder: Saved/Checkpoints/{model_name}/{branch_name}/
    save_dir = settings.checkpoint_dir / settings.model_name / branch_name
    save_dir.mkdir(parents=True, exist_ok=True)

    filepath = save_dir / f"step_{step:06d}.gguf"

    writer = gguf.GGUFWriter(str(filepath), "llama")

    # Save all model weights
    for name, param in model.state_dict().items():
        writer.add_tensor(name, param.detach().cpu().numpy())

    # Dynamic metadata
    metadata: Dict[str, Any] = {
        "versai.step": step,
        "versai.model_name": settings.model_name,
        "versai.branch_name": branch_name,
    }

    config_obj = getattr(model, "config", None)
    if config_obj is not None:
        if hasattr(config_obj, "model_dump"):
            config_dict = config_obj.model_dump()
        else:
            config_dict = (
                vars(config_obj)
                if hasattr(config_obj, "__dict__")
                else dict(config_obj)
            )
        for key, value in config_dict.items():
            metadata[f"versai.config.{key}"] = value

    if extra_metadata:
        for key, value in extra_metadata.items():
            metadata[f"versai.{key}"] = value

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

    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    writer.write_tensors_to_file()
    writer.close()

    print(f"GGUF saved: {filepath}")


def load_from_gguf(filepath: str | Path, model: torch.nn.Module) -> Dict[str, Any]:
    """Load weights and metadata from GGUF checkpoint."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Checkpoint not found: {filepath}")

    reader = gguf.GGUFReader(str(filepath))

    state_dict = {}
    for tensor in reader.tensors:
        state_dict[tensor.name] = torch.from_numpy(tensor.data)

    model.load_state_dict(state_dict, strict=False)
    print(f"Loaded checkpoint: {filepath}")

    metadata = {}
    for field in reader.fields.values():
        if field.name.startswith("versai."):
            metadata[field.name] = field.data

    return metadata
