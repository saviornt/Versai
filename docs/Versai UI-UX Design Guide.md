# **UI/UX Design Document v1.7** 

**Versai â€“ Procedural Vibe Training Simulator**  
**Document Version:** 1.7 (April 28, 2026\)  
**Status:** Active â€“ Living blueprint for all UI/UX implementation (base game \+ Game Feature Plugins)  
**File Location:** `docs/UI_UX_Design_Document.md`

**References:**

- Game Design Document (GDD) v2.0  
- Models\_DLC.md v2.0 (Game Feature Plugin system)  
- Architecture Design Document v4.0  
- PCG\_Niagara\_Hybrid\_Design.md  
- UE5\_Optimization\_Guide.md v1.1  
- Python\_Playground\_API.md v1.0  
- SharedMemory\_StructuredBuffer\_Design.md v2.0  
- GitHub repo: [https://github.com/saviornt/Versai](https://github.com/saviornt/Versai)

---

## 1\. Vision & Philosophy

Versaiâ€™s UI/UX must feel like part of the living intelligence â€” the control surface of â€œThe Verseâ€ (the official name for the procedurally generated environment). The Verse is a dynamic, player-chosen manifestation of the neural networkâ€™s training state. It can be a vast galaxy-filled universe, a neon-drenched cyberpunk megacity, a lush fantasy realm, a microscopic quantum landscape, or any other imaginable world.

### Core Pillars

- Immersive yet Non-Intrusive  
- Futuristic, Fun, & Engaging  
- Reactive & Living  
- Modular & Community-Driven  
- Performance-First (60+ FPS on RTX 3080-class)

### Core Fantasy

*Train intelligence. Watch reality form.*

In Versai, every dataset, model, and training decision reshapes a living reality called The Verse. It might become a galaxy. A city. A strange evolving system that behaves like nothing youâ€™ve seen before.

You donâ€™t just watch it grow, you teach it how to exist.

Because beneath it all is something real:  
**An AI is being born in real-time.**

The world you see is not fiction. You are not observing a simulation. Versai is not just intelligence made visible, but *interactive*.

---

## 2\. Theming System

All themes in Versai are implemented as Game Feature Plugins. This makes every visual, interactive, and auditory style fully modular, hot-swappable, and community-extensible.

### 2.1 Core UI/UX Template (Base Game)

The Core UI/UX Template is the foundational structure that ships inside the base game. It is **not** a Game Feature Plugin.

It contains all base classes and systems required for the entire experience:

- Master widget hierarchy (`UMG_VersaiBaseTemplate`)  
- Common UI elements and reusable components  
- Base PCG Graph and Niagara systems for The Verse (minimal â€œCosmic Verseâ€ fallback)  
- Base sound classes and MetaSounds integration  
- All NDI bindings (`UNiagaraDataInterfaceVersai`) for telemetry-driven reactivity

The template is intentionally generic and extensible. It provides every core piece of functionality (HUD layout, Verse selector carousel, telemetry graphs, intervention widgets, plugin browser) while exposing clean override points for Game Feature Plugins.

### 2.2 UI Packs (Game Feature Plugins)

UI Packs are Game Feature Plugins that modify the Core UI/UX Template at runtime.  
The base game ships with three UI Packs:

- Light Mode  
- Dark Mode  
- System (automatically follows Windows 11 accent color \+ light/dark setting)

Any additional community UI Packs follow the same pattern and override style sets, MPC values, widget subclasses, and Niagara UI particles.

### 2.3 Verse Theme Plugins (Game Feature Plugins)

Verse Themes are first-class Game Feature Plugins (exactly like UI Packs). They modify the Core UI/UX Template at runtime by:

- Overriding the active PCG Graph (`PCG_VerseTheme_XXX`)  
- Swapping/overriding the primary Niagara System (`NS_VerseTheme_XXX`)  
- Remapping NDI User Parameters (density â†’ building height for NeonSprawl, gradient\_mag â†’ nebula intensity for Cosmic Verse, etc.)  
- Optionally overriding specific template widgets (e.g., custom holographic panel materials, theme-specific intervention popups)

**Folder Structure**

| Versai/Plugins/â””â”€â”€ Verse-NeonSprawl-v1/    â”œâ”€â”€ manifest.json    â”œâ”€â”€ Content/    â”‚   â”œâ”€â”€ PCG/                            â† overrides base PCG graph    â”‚   â”œâ”€â”€ Niagara/                        â† overrides base Niagara system    â”‚   â”œâ”€â”€ Materials/                      â† template overrides    â”‚   â””â”€â”€ Textures/ |
| :---- |

**manifest.json**

| {  "type": "verse\_theme",  "name": "NeonSprawl",  "version": "1.0",  "description": "Cyberpunk megacity \- overrides PCG graph and Niagara system in the Core UI/UX Template",  "pcg\_graph": "PCG\_NeonSprawl",  "niagara\_system": "NS\_VerseNeonSprawl",  "template\_overrides": \["MPC\_VersaiUI", "UMG\_VersePanel"\],  "default\_for\_style": \["adversarial"\],  "tags": \["cyberpunk", "city", "neon"\]} |
| :---- |

**Hot-Swap Behavior**

Loaded via `UPluginManager` \+ `UGameFeaturePlugin`. `APCGVersaiUniverseActor` and the base HUD call `ApplyVerseThemeOverride()` to apply targeted modifications to the Core UI/UX Template. Training loop continues uninterrupted (`VersaiStructuredBuffer` unchanged). The game always falls back to the Core UI/UX Template if no Verse Theme is active.

### 2.4 Audio Theme Packs (Game Feature Plugins)

Audio Theme Packs are first-class Game Feature Plugins that modify the sonification layer of the Core UI/UX Template. They override the MetaSounds-driven audio engine and NDI bindings to create unique ambient soundscapes that react to the same telemetry data.

**Folder Structure**

| Versai/Plugins/â””â”€â”€ Sound-EtherealDrift-v1/    â”œâ”€â”€ manifest.json    â”œâ”€â”€ Content/    â”‚   â”œâ”€â”€ MetaSounds/          â† overrides for S\_VersaiSonification    â”‚   â”œâ”€â”€ Niagara/             â† optional audio-reactive emitters    â”‚   â””â”€â”€ Audio/ |
| :---- |

**manifest.json** example

| {  "type": "audio\_theme\_pack",  "name": "EtherealDrift",  "version": "1.0",  "description": "Dream-like resonant tones that evolve with embedding convergence",  "metasound\_graph": "MS\_EtherealDrift",  "template\_overrides": \["MS\_VersaiSonification"\],  "tags": \["ambient", "ethereal", "meditative"\]} |
| :---- |

Audio Theme Packs are fully hot-swappable and can be combined with any UI Pack or Verse Theme.

---

## 3\. Core User Flows & Screens

### 3.1 Main Menu (Observatory Hub)

Full-screen preview of the currently selected Verse (small PCG subset \+ Niagara demo driven by dummy telemetry, using the Core UI/UX Template). Holographic orb menu expands with â€œNew Verseâ€ as the hero button.

### 3.2 Training Configuration Screen (New Verse Creation)

Prominent Verse Theme Selector (star of the UX): horizontal carousel / grid of theme cards (all rendered through the Core UI/UX Template with per-theme overrides applied on preview).  
Each card includes:

- Thumbnail (live miniature Niagara/PCG preview)  
- Theme name \+ short poetic description  
- â€œWatch Demoâ€ button â†’ spawns floating holographic window with animated Verse (5-second loop)  
  Dropdown fallback for accessibility / keyboard users (populated from loaded Verse plugins).  
  Default: Cosmic Verse.  
  One-click â€œCreate New Verseâ€ starts training with the chosen theme, model, and style.

### 3.3 In-Universe HUD (Primary Gameplay View)

All HUD panels are instances of the Core UI/UX Template. Verse Theme Plugins, HUD Packs, and Audio Theme Packs modify only their respective layers while preserving the templateâ€™s layout and reactivity logic.

Top-center quick-switch carousel for Verse Themes (same cards, smaller).  
Minimal state shows the current Verse name with a tiny animated icon that pulses with training telemetry.

### 3.4 Plugin Browser (Models \+ UI Packs \+ Verse Themes \+ Audio Theme Packs)

Tabbed view: Models | HUD Packs | Verse Themes | Audio Theme Packs.  
Each pack previews the Core UI/UX Template after applying that pluginâ€™s overrides.

---

## 4\. The Verse â€“ Procedural Environment Themes

**Official Name**: â€œThe Verseâ€ â€“ the living, procedurally generated environment that is the visual embodiment of your neural networkâ€™s training.

**Verse Selection (Creative Definition Layer)**  
*The Verse defines how intelligence becomes visible as it learns.*

Before training begins, the player defines how intelligence will manifest visually as it learns.

This is not a cosmetic theme system.  
It is a representation layer for the structure of learning itself.

Each Verse determines how the underlying training process is interpreted spatially within the world.

Examples include:

* Cosmic (galaxies, nebulae, black holes, star systems)  
* Cyberpunk (cities, networks, data highways)  
* Biologic (ecosystems, cellular growth, organic structures)  
* Abstract (non-Euclidean forms, latent-space geometry)

The selected Verse becomes the lens through which the modelâ€™s learning process is rendered and experienced.

**Core Mapping Principle**  
Each Verse defines how machine learning dynamics are visually expressed:

* Embeddings â†’ spatial clustering and structure formation  
* Attention â†’ connectivity, flow, and relational linking  
* Gradients / Loss â†’ environmental instability, transformation pressure, or energy flow  
* Training Progress â†’ expansion, evolution, and structural complexity over time

**Extensibility**  
The base game ships with a single Verse: Cosmic Verse.

Community-created Verse Themes are distributed as Game Feature Plugins, allowing entirely new representational systems to be added without modifying core logic.

Examples:

* Steampunk Sky-Fleet  
* Underwater Bioluminescent Abyss  
* Post-Apocalyptic Wasteland

**Technical Mapping**  
Verse rendering is driven through a modular PCG \+ Niagara system pipeline.

UNiagaraDataInterfaceVersai exposes:

* VerseThemeID  
* Attribute remapping layers for visual interpretation of training state  
* Real-time binding between ML telemetry and procedural world generation

---

## 5\. Interaction & Feedback Patterns

- Input: Mouse \+ Keyboard primary (WASD camera fly in universe). Future gamepad support.  
- Feedback: Every UI action triggers a subtle Niagara spark or MetaSound â€œconfirmation toneâ€ mapped to current attention mean.  
- Dynamic Reactivity: High loss â†’ panels get slight â€œturbulenceâ€ (material distortion). Converging embeddings â†’ clean resonant glows. Player proximity to a galaxy cluster â†’ contextual HUD pops up with neuron details.  
- Accessibility: Full color-blind modes per theme, scalable text, reduced motion toggle, high-contrast mode.

---

## 6\. UE5 Technical Implementation Guidelines

- Primary UI Framework: UMG \+ custom `UUserWidget` subclasses built on the Core UI/UX Template.  
- Styling: `UStyleSet_VersaiUniversal` \+ `MPC_VersaiUI` (Core UI/UX Template). All Game Feature Plugins (HUD Packs, Verse Themes, Audio Theme Packs) provide targeted overrides via UE5 Game Feature Plugin asset rules (soft references, material instances, style overrides).  
- Performance: All overrides are zero-cost at runtime (pre-cached material parameter collections, pooled widgets). Follow UE5\_Optimization\_Guide.md CVars for UMG.  
- Niagara UI Integration: Core UI/UX Template includes optional â€œUI Particlesâ€ layer; plugins modify emitter parameters via NDI.

---

## 7\. Accessibility & Inclusivity

- Full screen-reader support via UMG accessibility tags.  
- Color-blind presets (Deuteranopia, Protanopia, Tritanopia) per theme.  
- Reduced motion / photo-sensitivity toggle.  
- Font scaling \+ high-contrast mode.  
- Keyboard-only navigation everywhere.

---

## 8\. Implementation Roadmap (Ready-to-Drop Kanban Cards)

**Phase 1 â€“ Base HUD & Themes \+ Verse Selector (Sprint 2, target May 15\)**

- Implement Core UI/UX Template (`UMG_VersaiBaseTemplate`, `MPC_VersaiUI`, `UStyleSet_VersaiUniversal`).  
- Implement `UMG_VersaiVerseSelector` widget (renders through Core UI/UX Template \+ plugin overrides).  
- Wire `ApplyVerseThemeOverride()` on `APCGVersaiUniverseActor` for runtime PCG/Niagara swaps.

**Phase 2** \- HUD Theme Plugin loader (Base Game UI \-\> Light / Dark / System)

**Phase 3** â€“ Verse Theme Plugin loader (Base Game theme \-\> Universal Theme

**Phase 4** â€“ Audio Theme Plugin loader (Base Game theme \-\> Audio Theme (to be renamed)

**Phase 5** â€“ Full In-Universe Reactivity & Polish.

**Post-MVP Phase 1**

- In-engine **Theme Designer** â€“ players create and save their own custom themes directly inside Versai (no external tools required).  
- In-engine **Model Designer** â€“ players create their own machine learning algorithms, weights, inference patterns, and training hooks without needing Visual Studio or external IDEs.

**Phase 4** â€“ Community & Marketplace Integration (Post-MVP).  


