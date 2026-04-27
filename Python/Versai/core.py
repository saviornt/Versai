import argparse
import importlib
import sys
from pathlib import Path


from Versai.settings import settings
from Versai.shared_memory import VersaiSharedBuffer


def parse_args():
    parser = argparse.ArgumentParser(description="Versai Training Core")
    parser.add_argument(
        "--plugin",
        type=str,
        default=None,
        help="Game Feature Plugin name (e.g. CausalLM)",
    )
    parser.add_argument(
        "--load-checkpoint",
        type=str,
        default=None,
        help="Path to GGUF checkpoint to continue from",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default=None,
        help="Branch name to use (auto-incremented if main exists and no checkpoint is loaded)",
    )
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
    """Auto-increment branch name if 'main' already exists and we are starting fresh."""
    base_dir = settings.checkpoint_dir / model_name
    if not base_dir.exists():
        return "main"

    if not (base_dir / "main").exists():
        return "main"

    # Find highest branch-N
    i = 1
    while (base_dir / f"branch-{i}").exists():
        i += 1
    return f"branch-{i}"


def load_plugin_trainer(plugin_name: str):
    plugin_path = (
        Path(__file__).parent.parent.parent
        / "Plugins"
        / "GameFeatures"
        / plugin_name
        / "Python"
    )
    if not plugin_path.exists():
        raise FileNotFoundError(f"Plugin not found: {plugin_path}")

    sys.path.insert(0, str(plugin_path))
    trainer_module = importlib.import_module(f"{plugin_name}.trainer")
    return trainer_module.run_training


def main():
    args = parse_args()

    plugin_name = args.plugin or settings.active_plugin
    model_name = settings.model_name

    # Determine branch name
    if args.load_checkpoint:
        branch_name = settings.branch_name  # keep current branch when loading
    elif args.branch:
        branch_name = args.branch
    else:
        branch_name = get_next_branch_name(model_name)

    # Update settings for this run
    settings.branch_name = branch_name

    print("Versai Training Core")
    print(f"   Plugin: {plugin_name}")
    print(f"   Model:  {model_name}")
    print(f"   Branch: {branch_name}")
    print(f"   Max steps: {args.max_steps if args.max_steps else 'Unlimited'}")

    run_training = load_plugin_trainer(plugin_name)

    telemetry = VersaiSharedBuffer()

    if args.load_checkpoint:
        print(f"   Loading checkpoint: {args.load_checkpoint}")

    run_training(
        telemetry_buffer=telemetry,
        max_steps=args.max_steps,
        checkpoint_every_steps=args.checkpoint_every_steps,
        checkpoint_every_minutes=args.checkpoint_every_minutes,
        load_checkpoint=args.load_checkpoint,
    )


if __name__ == "__main__":
    main()
