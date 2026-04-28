from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


PLUGIN_DIR = Path(__file__).parent
MANIFEST_PATH = PLUGIN_DIR / "manifest.json"


class PluginMetadata(BaseModel):
    """Static plugin metadata loaded from manifest.json."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    display_name: str
    version: str
    description: str
    compatible_with: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class GameMetadata(BaseModel):
    """Game-facing metadata used by The Verse and MetaSounds bindings."""

    model_config = ConfigDict(extra="forbid", strict=True)

    default_verse_theme: str
    default_audio_theme: str
    hud_modes: list[str] = Field(default_factory=list)
    telemetry_profile: str
    audio_parameter_profile: str


class GGUFMetadata(BaseModel):
    """GGUF export metadata defaults owned by the plugin manifest."""

    model_config = ConfigDict(extra="forbid", strict=True)

    architecture: str
    model_name: str
    training_style_id: str
    metadata_prefix: str = "versai"
    export_tags: list[str] = Field(default_factory=list)


class TrainingMetadata(BaseModel):
    """Training configuration resolved from the plugin manifest."""

    model_config = ConfigDict(extra="forbid", strict=True)

    method: str
    type: str
    vocab_size: int
    d_model: int
    n_heads: int
    n_layers: int
    feedforward_multiplier: int
    batch_size: int
    seq_length: int
    learning_rate: float
    dropout: float
    activation_function: str
    batch_first: bool
    norm_first: bool
    bias: bool


class CausalLMManifest(BaseModel):
    """Authoritative plugin manifest loaded once per training start."""

    model_config = ConfigDict(extra="forbid", strict=True)

    plugin: PluginMetadata
    game: GameMetadata
    gguf: GGUFMetadata
    training: TrainingMetadata

    @classmethod
    def load(cls, path: Path | None = None) -> "CausalLMManifest":
        """Load the manifest snapshot used for the current training run."""
        manifest_path = path or MANIFEST_PATH
        with manifest_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return cls.model_validate(payload)

    def to_gguf_metadata(self) -> dict[str, Any]:
        """Flatten manifest metadata for GGUF export under versai.* keys."""
        return {
            "plugin.name": self.plugin.name,
            "plugin.display_name": self.plugin.display_name,
            "plugin.version": self.plugin.version,
            "plugin.description": self.plugin.description,
            "plugin.compatible_with": json.dumps(self.plugin.compatible_with),
            "plugin.tags": json.dumps(self.plugin.tags),
            "game.default_verse_theme": self.game.default_verse_theme,
            "game.default_audio_theme": self.game.default_audio_theme,
            "game.hud_modes": json.dumps(self.game.hud_modes),
            "game.telemetry_profile": self.game.telemetry_profile,
            "game.audio_parameter_profile": self.game.audio_parameter_profile,
            "gguf.architecture": self.gguf.architecture,
            "gguf.model_name": self.gguf.model_name,
            "gguf.training_style_id": self.gguf.training_style_id,
            "gguf.export_tags": json.dumps(self.gguf.export_tags),
            "training.method": self.training.method,
            "training.type": self.training.type,
        }


class CausalLMConfig(BaseModel):
    """Resolved backend config snapshot for the active CausalLM run."""

    model_config = ConfigDict(extra="forbid", strict=True)

    plugin_name: str
    plugin_display_name: str
    plugin_version: str
    model_name: str
    training_style_id: str
    default_verse_theme: str
    default_audio_theme: str
    telemetry_profile: str
    audio_parameter_profile: str
    compatible_with: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    vocab_size: int
    d_model: int
    n_heads: int
    n_layers: int
    feedforward_multiplier: int
    batch_size: int
    seq_length: int
    learning_rate: float
    dropout: float
    activation_function: str
    batch_first: bool
    norm_first: bool
    bias: bool

    @classmethod
    def from_manifest(
        cls, manifest: CausalLMManifest | None = None
    ) -> "CausalLMConfig":
        """Resolve the immutable config snapshot for one training session."""
        current_manifest = manifest or CausalLMManifest.load()
        return cls(
            plugin_name=current_manifest.plugin.name,
            plugin_display_name=current_manifest.plugin.display_name,
            plugin_version=current_manifest.plugin.version,
            model_name=current_manifest.gguf.model_name,
            training_style_id=current_manifest.gguf.training_style_id,
            default_verse_theme=current_manifest.game.default_verse_theme,
            default_audio_theme=current_manifest.game.default_audio_theme,
            telemetry_profile=current_manifest.game.telemetry_profile,
            audio_parameter_profile=current_manifest.game.audio_parameter_profile,
            compatible_with=current_manifest.plugin.compatible_with,
            tags=current_manifest.plugin.tags,
            vocab_size=current_manifest.training.vocab_size,
            d_model=current_manifest.training.d_model,
            n_heads=current_manifest.training.n_heads,
            n_layers=current_manifest.training.n_layers,
            feedforward_multiplier=current_manifest.training.feedforward_multiplier,
            batch_size=current_manifest.training.batch_size,
            seq_length=current_manifest.training.seq_length,
            learning_rate=current_manifest.training.learning_rate,
            dropout=current_manifest.training.dropout,
            activation_function=current_manifest.training.activation_function,
            batch_first=current_manifest.training.batch_first,
            norm_first=current_manifest.training.norm_first,
            bias=current_manifest.training.bias,
        )


def load_manifest(path: Path | None = None) -> CausalLMManifest:
    """Return the authoritative manifest snapshot for the plugin."""
    return CausalLMManifest.load(path)
