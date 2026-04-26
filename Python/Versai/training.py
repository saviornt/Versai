import torch
import torch.nn as nn
import time
from pathlib import Path

from .config import TrainingConfig, DEFAULT_CONFIG
from .model import AmbienceTransformer
from .shared_memory import VersaiSharedBuffer
from .gguf_exporter import save_to_gguf
from .data_loader import get_dummy_batch


def training_loop(config: TrainingConfig = None):
    if config is None:
        config = DEFAULT_CONFIG

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Versai Training Core — {config.style.upper()} (Self-Supervised Fluency)")
    print(
        f"   Device: {device} | Model: {config.model_name} | Checkpoint dir: {config.checkpoint_dir}"
    )

    # === Model creation + torch.compile (this eliminates the unfused warning) ===
    model = AmbienceTransformer(config).to(device)

    if device == "cuda":
        print("🔥 Applying torch.compile() for FlexAttention fusion...")
        model = torch.compile(
            model,
            mode="reduce-overhead",  # best for real-time training loops
            fullgraph=False,  # safer with our telemetry hook
            dynamic=False,
        )

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)

    telemetry = VersaiSharedBuffer(config)

    step = 0
    try:
        while True:
            x = get_dummy_batch(config, device)
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

            if step % config.checkpoint_interval == 0 or (
                loss.item() < config.save_on_stable_loss and step > 100
            ):
                save_to_gguf(model, config, step)

            step += 1
            time.sleep(0.008)

    except KeyboardInterrupt:
        print("\n🛑 Training stopped by user")
    finally:
        telemetry.close()
        print("✅ Training core shutdown clean")


if __name__ == "__main__":
    training_loop()
