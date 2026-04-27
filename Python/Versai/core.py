import argparse
import importlib
import sys
from pathlib import Path
from typing import Literal

from Versai.settings import settings
from Versai.structured_buffer import VersaiStructuredBuffer


def parse_args():
    """Parse command-line arguments for Versai Training Core.

    Supports the exact command you ran: --plugin CausalLM --mode train
    """
    parser = argparse.ArgumentParser(description="Versai Training Core")
    parser.add_argument(
        "--plugin",
        type=str,
        default=None,
        help="Game Feature Plugin name (e.g. CausalLM)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="train",
        choices=["train", "inference"],
        help="Operation mode (train or inference)",
    )
    parser.add_argument(
        "--load-checkpoint",
        type=str,
        default=None,
        help="Path to GGUF checkpoint to continue from",
    )
    parser.add_argument("--branch", type=str, default=None, help="Branch name to use")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Maximum number of training steps (None = unlimited)",
    )
    parser.add_argument("--checkpoint-every-steps", type=int, default=200)
    parser.add_argument("--checkpoint-every-minutes", type=float, default=None)
    return parser.parse_args()


def get_next_branch_name(model_name: str) -> str:
    """Auto-increment branch name if main already exists and we are starting fresh."""
    base_dir = settings.checkpoint_dir / model_name
    if not base_dir.exists() or not (base_dir / "main").exists():
        return "main"

    i = 1
    while (base_dir / f"branch-{i}").exists():
        i += 1
    return f"branch-{i}"


def load_plugin_trainer(plugin_name: str):
    """Dynamically load the trainer from a Game Feature Plugin."""
    versai_root = Path(__file__).parent.parent.parent
    if str(versai_root) not in sys.path:
        sys.path.insert(0, str(versai_root))

    plugin_path = (
        Path(__file__).parent.parent.parent
        / "Plugins"
        / "GameFeatures"
        / plugin_name
        / "Python"
    )
    if not plugin_path.exists():
        raise FileNotFoundError(f"Plugin not found: {plugin_path}")

    if str(plugin_path) not in sys.path:
        sys.path.insert(0, str(plugin_path))

    # Flat import — trainer.py is in the Python/ folder itself
    trainer_module = importlib.import_module("trainer")
    return trainer_module.run_training


def main():
    args = parse_args()

    plugin_name = args.plugin or settings.active_plugin
    model_name = settings.model_name

    # Determine branch name once per run
    if args.load_checkpoint:
        branch_name = settings.branch_name
    elif args.branch:
        branch_name = args.branch
    else:
        branch_name = get_next_branch_name(model_name)

    settings.branch_name = branch_name

    print("Versai Training Core")
    print(f"   Plugin: {plugin_name}")
    print(f"   Mode:   {args.mode}")
    print(f"   Model:  {model_name}")
    print(f"   Branch: {branch_name}")
    print(f"   Max steps: {args.max_steps if args.max_steps else 'Unlimited'}")
    if args.load_checkpoint:
        print(f"   Loading checkpoint: {args.load_checkpoint}")

    run_training = load_plugin_trainer(plugin_name)

    telemetry = VersaiStructuredBuffer()

    # Future-proof mode handling (match/case per coding rules)
    match args.mode:
        case "train":
            run_training(
                telemetry_buffer=telemetry,
                max_steps=args.max_steps,
                checkpoint_every_steps=args.checkpoint_every_steps,
                checkpoint_every_minutes=args.checkpoint_every_minutes,
                load_checkpoint=args.load_checkpoint,
            )
        case "inference":
            print("Inference mode not yet implemented - coming in Phase 3")
            # run_inference(...)  # TODO
        case _:
            raise ValueError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()
