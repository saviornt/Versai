import torch
import torch.nn as nn
import time
import sys
from pathlib import Path
from typing import Optional

plugin_dir = Path(__file__).parent
project_root = plugin_dir.parent.parent.parent.parent

sys.path.insert(0, str(plugin_dir))
sys.path.insert(0, str(project_root / "Python"))

from config import CausalLMConfig  # noqa E402
from model import CausalLMModel  # noqa E402

from Versai.structured_buffer import VersaiStructuredBuffer  # pyright: ignore[reportMissingImports] # noqa E402
from Versai.gguf_fileops import save_to_gguf, load_from_gguf  # pyright: ignore[reportMissingImports] # noqa E402
from Versai.data.data_loader import get_dataloader  # pyright: ignore[reportMissingImports] # noqa E402


def run_training(
    telemetry_buffer: Optional[VersaiStructuredBuffer] = None,
    config: Optional[CausalLMConfig] = None,
    max_steps: Optional[int] = None,
    checkpoint_every_steps: int = 200,
    checkpoint_every_minutes: Optional[float] = None,
    load_checkpoint: Optional[str] = None,
) -> None:
    if config is None:
        config = CausalLMConfig()

    # match case for cuda, amd, or mps (macos/metal)
    match True:
        case _ if torch.cuda.is_available():
            device = "cuda"
        case _ if torch.backends.mps.is_available():
            device = "mps"
        case _:
            device = "cpu"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"CausalLM Training Started on {device}")

    model = CausalLMModel(config).to(device)

    # Load checkpoint if provided
    start_step = 0
    if load_checkpoint:
        metadata = load_from_gguf(load_checkpoint, model)
        start_step = metadata.get("versai.step", 0)
        print(f"Continued training from step {start_step}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)

    telemetry = telemetry_buffer or VersaiStructuredBuffer()

    # Get the dataset to train on
    dataloader = get_dataloader(batch_size=config.batch_size)
    dataloader_iter = iter(dataloader)

    step = start_step
    start_time = time.time()
    last_checkpoint_time = start_time

    try:
        while True:
            if max_steps is not None and step >= max_steps:
                print(f"Reached max_steps ({max_steps}). Stopping training.")
                break

            try:
                batch = next(dataloader_iter)
            except StopIteration:
                dataloader_iter = iter(dataloader)
                batch = next(dataloader_iter)

            x = (
                batch["text"].to(device)
                if isinstance(batch["text"], torch.Tensor)
                else torch.randint(
                    0,
                    config.vocab_size,
                    (config.batch_size, config.seq_length),
                    device=device,
                )
            )
            target = x[:, 1:]

            output = model(x, telemetry)
            logits = output[:, :-1].reshape(-1, config.vocab_size)
            loss = nn.CrossEntropyLoss()(logits, target.reshape(-1))

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            telemetry.write_telemetry(
                loss=loss.item(),
                embeddings_norm=model.embeddings.weight.norm().item(),
                attention_max=0.0,
            )

            if step % 20 == 0:
                print(f"Step {step:05d} | Loss: {loss.item():.4f}")

            if step % checkpoint_every_steps == 0 and step > 0:
                save_to_gguf(model, step)

            if checkpoint_every_minutes is not None:
                elapsed = (time.time() - last_checkpoint_time) / 60.0
                if elapsed >= checkpoint_every_minutes:
                    save_to_gguf(model, step)
                    last_checkpoint_time = time.time()

            step += 1
            time.sleep(0.008)

    except KeyboardInterrupt:
        print("Training stopped by user (Ctrl+C)")
        print("Saving final checkpoint...")
        save_to_gguf(model, step)
    finally:
        telemetry.close()
        print("CausalLM training shutdown clean")


if __name__ == "__main__":
    run_training(max_steps=1000)
