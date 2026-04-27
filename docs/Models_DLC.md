# Versai Post-MVP Feature Plugin System: Models as DLC

**Design Document**
**Version:** 1.0 (April 26, 2026)
**Project Name:** Versai – Procedural Vibe / Ambience Training Simulator
**Author:** Grok (Lead Dev) + Dave (Human-in-the-Loop)
**Status:** Post-MVP / DLC Expansion Phase
**File Location:** `Versai/Sources/Design/Plugins/Models_DLC.md` (living document)

## 1. Vision & High-Level Pitch

**Versai Models as DLC turns every trained universe into a shareable, installable “Game Feature Plugin”** — a complete, self-contained package that players can download, drop into their game, and instantly load as a new living intelligence with its own visual/auditory ambience, training style, and inference personality.

**Core Fantasy:**  
Players don’t just *train* models — they **collect, trade, and evolve entire universes**. A Model DLC is like a trading card, a musical instrument, and a living AI companion all in one. The community becomes co-creators of intelligence.

**Player Experience Goals:**

- Instant gratification: drop a `.versaiplugin` folder → new universe appears in the menu
- Creative expression: package your best custom-trained model + ambience preset
- Social / marketplace layer: share on Steam Workshop, itch.io, or in-game gallery
- Deep ownership: each model carries its training history, metadata, and “ambience signature”
- Post-launch monetization & community longevity (free core + premium DLC packs)

**One-Sentence Logline:**

“Every GGUF model you sculpt in Versai can become a beautiful, plug-and-play DLC that brings its own procedural universe, sonification, and training style into any player’s game.”

## 2. Core Features of a Model DLC Plugin

| Feature | Description | MVP for Plugin System |
|---------|-------------|-----------------------|
| **Weights (GGUF)** | The actual quantized model file | Must-have |
| **Training Algorithm** | Optional `training_style.py` with custom loss / hook | High |
| **Inference Parameters** | Temperature, top-p, system prompt, personality tokens | Must-have |
| **Ambience Preset** | Niagara system + sonification map that reacts to this model | High |
| **Metadata & Lore** | Embedded training history, creator notes, “universe seed” | Must-have |
| **Thumbnail / Visual Identity** | Custom particle system preview or static image | Medium |
| **Hot-Swap Support** | Load/unload at runtime without restarting training | Must-have |
| **Versioning & Compatibility** | Manifest enforces engine version + PyTorch compat | Must-have |

## 3. Plugin Package Specification (Folder Structure)

```text
Versai/Plugins/
└── CausalLM-{32bit_hash}/                    ← Plugin folder name (unique ID)
    ├── Python/                               ← Python Model Scripts
        ├── manifest.json                     ← Required metadata
        ├── model.gguf                        ← Core weights (can be multiple for MoE later)
        ├── trainer.py                        ← Training algorithm
        ├── config.json                       ← Generation & personality settings
        ├── README.md                         ← Model documentation
    ├── Content/                              ← UE5 Content Folder
        ├── ambience_preset/                  ← Visual + audio identity presets
        │   ├── niagara_system.uasset         ← UE5 Niagara asset (or .niagara file)
        │   ├── pcg_graph.uasset              ← UE5 PCG asset
        │   ├── sonification_map.json         ← Hierarchical mapping for this model
        │   └── preview_thumbnail.png
        ├── lore.md                           ← Optional flavor text / story
        └── icon.png                          ← Menu icon
```

**manifest.json example:**

```json
{
  "name": "MyCosmicOracle",
  "version": "1.2",
  "author": "Dave",
  "description": "A meditative oracle trained on ancient wisdom + star data",
  "versai_version": "1.0+",
  "style": "custom_meditation",
  "d_model": 512,
  "gguf_filename": "model.gguf",
  "pcg_graph": "cosmic_nebula",
  "ambience_preset": "cosmic_nebula",
  "tags": ["meditative", "wisdom", "space", "ambient"],
  "created": "2026-04-26",
  "featured_in": ["base_game", "dlc_pack_01"]
}
```

> Note: The above manifest needs to be updated/merged with the actual sample model's manifest.json for accuracy.

---

### 4. Integration with Core Versai Game

**In-Game Flow:**

1. **Plugin Browser** (main menu or in-universe “Observatory”) — scans `VersaiPlugins/` and `Saved/Plugins/`
2. **One-click Install** — copies folder + registers in SaveGame
3. **Hot-Swap** — from the HUD, player can switch active model mid-training or in inference mode
4. **Training Continuation** — if `training_style.py` exists, the core can continue training the model using the custom algorithm
5. **Ambience Sync** — Niagara Data Interface + sonification engine automatically load the plugin’s preset when the model is active

**SaveGame Integration:**

- UE5 `UVersaiSaveGame` stores an array of installed plugin IDs + active model reference
- Metadata (loss history, favorite interventions) is saved per plugin

**Multi-Model Support (future):**
- “Universe Merging” mode where two plugins can be blended (weighted average of embeddings + attention)

---

### 5. Technical Architecture

**Python Side (Training Core):**
- `plugin_loader.py` (new module) that reads `manifest.json` and dynamically imports `training_style.py` if present
- Extends `TrainingConfig` with `plugin_name` and `plugin_path`
- GGUF hot-loading via `gguf` + `torch.load_state_dict` (or direct GGUF → PyTorch conversion)

**UE5 Side:**
- `UPluginManager` C++ / Blueprint subsystem
- Custom `GameFeaturePlugin` system (UE5.7+ native support for modular content)
- Niagara Data Interface extended to accept plugin-specific emitters/ribbons
- Sonification engine reads `sonification_map.json` at runtime

**Security / Sandboxing:**
- Manifest validation on load
- Optional code signing for community plugins (future)

---

### 6. Development Roadmap (Post-MVP)

#### Phase A: Plugin Infrastructure (2 weeks)
- Manifest parser + loader
- Basic GGUF + inference config support
- Plugin Browser UI (Slate / UMG)

#### Phase B: Custom Training Styles (2 weeks)
- Dynamic `training_style.py` import + hook system
- Dave’s custom method becomes first official plugin

#### Phase C: Ambience Presets (1–2 weeks)
- Niagara + Sonification preset system

#### Phase D: Community & Marketplace (Ongoing)
- Steam Workshop integration
- In-game gallery / sharing
- Official DLC packs (e.g. “Protein Oracle”, “Code Muse”, “Dream Architect”)

**Milestone A:** “Plugin System Alive” — players can drop a folder and hot-swap models

---

### 7. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|----------|
| Large GGUF files bloating saves | Medium | Store only metadata in SaveGame; GGUF files live on disk |
| Malicious plugins (code execution) | Low | Manifest validation + optional sandbox for `training_style.py` |
| Version drift between plugins | Medium | Strict `versai_version` check + backward compat layer |
| Performance with many plugins | Low | Lazy loading + on-demand activation |

---

**This document is a living blueprint.**  
It will be updated at the end of every post-MVP sprint. All tasks are written as ready-to-drop Kanban cards.
