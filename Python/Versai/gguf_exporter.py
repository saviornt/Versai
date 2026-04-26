import gguf
import torch

from Versai.settings import settings


def save_to_gguf(model: torch.nn.Module, step: int):
    settings.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    filepath = settings.checkpoint_dir / f"causal_lm_step_{step:06d}.gguf"

    writer = gguf.GGUFWriter(str(filepath), "llama")

    for name, param in model.state_dict().items():
        writer.add_tensor(name, param.detach().cpu().numpy())

    # Metadata
    writer.add_key_value("versai.style", "causal_lm", gguf.GGUFValueType.STRING)
    writer.add_key_value("versai.step", step, gguf.GGUFValueType.INT32)
    writer.add_key_value("versai.d_model", settings.d_model, gguf.GGUFValueType.INT32)

    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    writer.write_tensors_to_file()
    writer.close()

    print(f"✅ GGUF saved: {filepath.name}")
