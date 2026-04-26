import torch
import torch.nn as nn
import time
import sys
from pathlib import Path
from typing import Optional

# Robust path setup
plugin_dir = Path(__file__).parent
project_root = plugin_dir.parent.parent.parent.parent

sys.path.insert(0, str(plugin_dir))
sys.path.insert(0, str(project_root / "Python"))

from config import CausalLMConfig  # noqa E402
from model import CausalLMModel  # noqa E402

from Versai.shared_memory import VersaiSharedBuffer  # pyright: ignore[reportMissingImports] # noqa E402
from Versai.gguf_exporter import save_to_gguf  # pyright: ignore[reportMissingImports] # noqa E402
from Versai.data_loader import get_dummy_batch  # pyright: ignore[reportMissingImports]  # noqa E402


def run_training(
    telemetry_buffer: Optional[VersaiSharedBuffer] = None,
    config: Optional[CausalLMConfig] = None,
    max_steps: Optional[int] = None,  # None = run forever
    checkpoint_every_steps: int = 200,
    checkpoint_every_minutes: Optional[float] = None,  # None = disabled
) -> None:
    """Thin trainer for CausalLM plugin.
    All control parameters are passed from the main backend (core.py)."""
    if config is None:
        config = CausalLMConfig()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"CausalLM Training Started on {device}")
    print(f"   Max steps: {max_steps if max_steps else 'Unlimited'}")
    print(f"   Auto-save every {checkpoint_every_steps} steps")
    if checkpoint_every_minutes:
        print(f"   Auto-save every {checkpoint_every_minutes} minutes")

    model = CausalLMModel(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001)

    telemetry = telemetry_buffer or VersaiSharedBuffer()

    step = 0
    start_time = time.time()
    last_checkpoint_time = start_time

    try:
        while True:
            if max_steps is not None and step >= max_steps:
                print(f"Reached max_steps ({max_steps}). Stopping training.")
                break

            x = get_dummy_batch()
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

            # Step-based checkpoint
            if step % checkpoint_every_steps == 0 and step > 0:
                save_to_gguf(model, step)

            # Time-based checkpoint
            if checkpoint_every_minutes is not None:
                elapsed = (time.time() - last_checkpoint_time) / 60.0
                if elapsed >= checkpoint_every_minutes:
                    save_to_gguf(model, step)
                    last_checkpoint_time = time.time()

            step += 1
            time.sleep(0.008)

    except KeyboardInterrupt:
        print("\nTraining stopped by user (Ctrl+C)")
        print("Saving final checkpoint on stop...")
        save_to_gguf(model, step)
    finally:
        telemetry.close()
        print("CausalLM training shutdown clean")


# Module-level test (for quick testing of the plugin in isolation)
if __name__ == "__main__":
    print("Testing CausalLM trainer module...")
    run_training(
        max_steps=1000,  # change to None for continuous
        checkpoint_every_steps=200,
        checkpoint_every_minutes=None,  # set to 5.0 for time-based saving
    )
