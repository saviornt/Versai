# Versai Post-MVP Feature Plugin System: Models as DLC

**Design Document**  
**Version:** 2.1 (April 28, 2026)  
**Project Name:** Versai  
**Status:** Post-MVP / DLC Expansion Phase  
**File Location:** `docs/Models_DLC.md`

## MVP Boundary Note

This document is intentionally post-MVP.

The MVP/Beta baseline ships with:

- one built-in model: `CausalLM`
- three HUD/UI packs: `Light`, `Dark`, `System`
- one official Verse theme: `Cosmic Verse`
- one official audio theme

Marketplace, model trading, and community DLC distribution begin after MVP/Beta.

---

## 1. Vision

Post-MVP, every trained model can become a shareable Game Feature Plugin with:

- model weights
- plugin metadata
- Verse identity
- audio identity
- training defaults
- GGUF export metadata

The long-term goal is to let players collect and evolve model-driven universes without destabilizing the shipped MVP runtime.

---

## 2. Plugin Package Structure

```text
Versai/Plugins/
└── MyCosmicOracle/
    ├── Python/
    │   ├── manifest.json
    │   ├── model.gguf
    │   ├── trainer.py
    │   └── README.md
    ├── Content/
    │   ├── PCG/
    │   ├── Niagara/
    │   ├── MetaSounds/
    │   └── UI/
    └── icon.png
```

---

## 3. Manifest Shape

The shipped MVP `CausalLM` plugin already uses `manifest.json` as the backend source of truth. Post-MVP DLC plugins should follow the same sectioned shape.

```json
{
  "plugin": {
    "name": "MyCosmicOracle",
    "display_name": "My Cosmic Oracle",
    "version": "1.2.0",
    "description": "A meditative oracle trained on ancient wisdom and star data.",
    "compatible_with": ["base_game"],
    "tags": ["meditative", "wisdom", "space", "ambient"]
  },
  "game": {
    "default_verse_theme": "Cosmic Verse",
    "default_audio_theme": "Oracle Drift",
    "hud_modes": ["Light", "Dark", "System"],
    "telemetry_profile": "cosmic_oracle",
    "audio_parameter_profile": "oracle_drift"
  },
  "gguf": {
    "architecture": "llama",
    "model_name": "my_cosmic_oracle",
    "training_style_id": "custom_meditation",
    "metadata_prefix": "versai",
    "export_tags": ["oracle", "post_mvp"]
  },
  "training": {
    "method": "transformers",
    "type": "decoder",
    "vocab_size": 32000,
    "d_model": 512,
    "n_heads": 8,
    "n_layers": 8,
    "feedforward_multiplier": 4,
    "batch_size": 16,
    "seq_length": 256,
    "learning_rate": 0.00005,
    "dropout": 0.1,
    "activation_function": "gelu",
    "batch_first": true,
    "norm_first": true,
    "bias": true
  }
}
```

Rules:

- `manifest.json` is authoritative for plugin-owned backend metadata and defaults.
- Player edits apply on next training start or plugin reload, not during an active run.
- GGUF export metadata should be derived from the resolved manifest snapshot.

---

## 4. Core Integration

Python side:

- load `manifest.json`
- resolve one immutable config snapshot per run
- load `trainer.py`
- export manifest-backed metadata into GGUF

UE side:

- use plugin identity to select Verse, UI, and MetaSound bindings
- keep DLC content isolated from MVP runtime stability
- validate compatibility before activation

---

## 5. Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Large GGUF files bloating saves | Medium | Keep GGUF files on disk and store only references/metadata in save data |
| Malicious plugin code | Medium | Manifest validation plus optional sandboxing/code signing post-MVP |
| Version drift between plugins | Medium | Explicit compatibility fields and backward-compat validation |
| Runtime instability from hot-swaps | Medium | Resolve plugin config once per activation and gate reload paths carefully |

---

This document is a living blueprint for the post-MVP plugin ecosystem and should remain aligned with the manifest-backed architecture established by the shipped `CausalLM` plugin.
