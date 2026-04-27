# Versai (In Active Development)

**Procedural Vibe / Ambience Training Simulator**

*Train a real AI using Machine Learning **as** the gameplay. Sculpt intelligence inside a living Niagara procedural universe that reacts in real time to loss, attention, gradients, and embeddings. Export polished GGUF models you can actually use.*

---

## 🎯 Vision

Versai turns neural network training into an immersive, meditative experience. You curate data, choose or invent training styles, watch a reactive cosmos of particles, ribbons, and vector storms evolve in real time, and intervene directly through the HUD. The better the training, the more harmonious and alive the universe becomes.

**Core Fantasy:** You are literally sculpting intelligence in a beautiful, reactive cosmos.

**One-Sentence Logline:**  
“Training a real LLM *is* the gameplay.”

---

## ✨ Core Features (MVP)

- **Real-Time Neural Training** — Live PyTorch 2.11 transformer with FlexAttention telemetry
- **Procedural Universe Visualization** — Niagara + custom UNiagaraDataInterface powered by shared GPU-friendly buffers
- **Generative Sonification** — WASAPI Exclusive Mode audio that maps embeddings → timbre, attention → harmonics, loss → texture
- **Training Styles** — Self-Supervised, Adversarial, Reinforcement + full custom `training_style.py` hooks
- **GGUF Checkpointing** — Auto-save with embedded ambience metadata
- **Hot-Swap & Plugin System** — Every trained model can become a shareable `.versaiplugin` (see [Models as DLC](./docs/Models_DLC.md))
- **Shared Memory Bridge** — Zero-copy, lock-free, double-buffered data flow between Python backend and UE5 (v3 architecture)

---

## 🏗️ Architecture (v3 – Single-Player GPU-Shared Memory)

```text
Python Backend (Training + Reduction)
         ↓ (Shared Memory – CPU/GPU buffers)
UE5 + Niagara (Real-time Rendering + Interaction)
```

- **Python** owns the training loop (PyTorch 2.11 + FlexAttention `score_mod` telemetry)
- **UE5** owns the visual cortex (C++ SharedMemoryReader → Niagara Data Interface)
- **Never** passes raw tensors — only reduced, GPU-friendly structs
- Fully decoupled: training never blocks rendering
- Double-buffered, frame-synced, zero dynamic allocation in hot path

Full details: [Architecture Design Document v3](./docs/Architecture%20Design%20Document_v3.md)

---

## 📁 Repository Structure

```text
Versai/
├── Python/                 # Training core, shared memory writer, GGUF exporter
├── Source/                 # UE5 C++ modules (CasualLM plugin scaffolding + NDI)
├── Plugins/                # Game Feature Plugins (CasualLM starter)
├── docs/                   # All living design documents
├── Config/                 # UE5 config
├── Content/Saved/          # Editor saves
└── Versai.uproject
```

---

## 🚀 Getting Started (Pre-Production Build)

### Prerequisites

- Windows 11 Pro
- Unreal Engine 5.7.4 (source-built recommended)
- Python 3.14 (free-threaded) + venv with PyTorch 2.11 cu130
- NVIDIA RTX 3080 or better (Ampere SM 8.6)

### Quick Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/saviornt/Versai.git
   cd Versai
   ```

2. Open `Versai.uproject` in Unreal Editor 5.7.4
3. Set up Python environment (see `Python/pyproject.toml` and `requirements.txt`)
4. Run `Python/launch_training.bat` (or launch via UE5 Python bridge)
5. Enter the universe and begin training

Detailed setup and Phase 0 environment lock instructions are in the design documents.

---

## 📋 Current Development Status

**Phase 0: Environment Lock** — Complete (April 26, 2026)  
**Phase 1: MVP Training Core** — In progress (CasualLM plugin scaffolding live)

See full roadmap in [Game Design Document](./docs/Game%20Design%20Document.md) and [Game Dev Plan](./docs/GameDevPlan_Versai.md).

---

## 📚 Documentation

All living documents are in the `/docs` folder:

- [Architecture Design Document v3](./docs/Architecture%20Design%20Document_v3.md)
- [Game Design Document](./docs/Game%20Design%20Document.md)
- [Models as DLC Plugin System](./docs/Models_DLC.md)
- [Game Dev Plan](./docs/GameDevPlan_Versai.md)

---

## 🔮 Post-MVP / DLC Vision

Every trained model becomes a shareable Game Feature Plugin with its own Niagara ambience preset, sonification map, training style hooks, and lore. Players collect, trade, and merge universes.

---

## 🤝 Contributing

This is a solo + human-in-the-loop project, but community input is welcome.  
Current focus: Phase 1 Training Core + Shared Memory Bridge.

- Fork & PRs against `main`
- All code follows strict Pydantic v2, Google-style docstrings, async-first Python 3.14, and zero-emoji policy
- See `Python/pyproject.toml` for linting and type-checking rules

---

**Versai** — Where training intelligence becomes the most beautiful game you’ve ever played.

*Last updated: April 26, 2026*  
*Lead Developer: Grok (with 20 years Unreal Engine 5 + ML experience)*

---

*Built with Unreal Engine 5.7, Python 3.14, PyTorch 2.11, and pure shared-memory passion.*
