# Versai Game Design Document (GDD)

**Version:** 2.0 (April 26, 2026)  
**Project Name:** Versai  
**Genre:** Procedural Vibe / Ambience Training Simulator  
**Target Platform:** Windows 11 Pro (PC)  
**Engine:** Unreal Engine 5.7.4 + Python 3.14 + PyTorch 2.11 (hybrid)  
**Team:** Solo + Human-in-the-Loop (Dave) + Lead Dev (Grok)  
**Status:** Pre-Production → MVP Sprint

---

## 1. Vision & High-Level Pitch (One-Sentence Logline)

**Versai is an immersive “vibe game” where training a real large language model *is* the gameplay.** Players upload their own data, choose (or invent) training styles, and watch a living procedural universe of embeddings, attention heads, and gradients evolve in real-time — visualized in Niagara, sonified through generative audio, and exported as a polished GGUF LLM they can actually use.

**Core Fantasy:** You are literally sculpting intelligence in a beautiful, reactive cosmos. The better the training, the more harmonious and alive the universe becomes.

**Player Experience Goals:**

- Relaxation + wonder (ambient “flow state”)
- Intellectual satisfaction (watching real ML happen)
- Creative ownership (custom data + custom training method)
- Tangible reward (export usable GGUF models)

---

## 2. Core Gameplay Loop (3–5 minutes repeatable)

1. **Load / Curate Data** → Text, protein sequences, sensor streams, or custom files.
2. **Select Training Style** → 4 core styles + your live custom method hook.
3. **Enter the Universe** → Real-time training loop begins.
4. **Observe & Sculpt** → Watch Niagara universe + sonification react to loss, attention, gradients.
5. **Intervene** → Adjust hyperparameters, inject new data, switch styles mid-training.
6. **Save / Export** → GGUF checkpoint with embedded “Ambience Metadata”.
7. **Repeat** → Hot-swap models, evolve further, or start new universes.

**Win Condition:** A beautiful, stable universe + a high-quality exportable LLM.

---

## 3. Key Features & Mechanics

| Feature | Description | MVP Priority |
|---------|-------------|--------------|
| **Real-Time Neural Training** | Live PyTorch transformer with FlexAttention telemetry | Must-have |
| **4 Training Styles + Custom** | Self-Supervised, Adversarial, Reinforcement, + Dave’s custom method | Must-have |
| **Procedural Universe (PCG+Niagara via UNiagaraDataInterface)** | Embeddings = particles, attention = ribbons/fog, gradients = vector storms | Must-have |
| **Generative Sonification** | WASAPI Exclusive Mode + hierarchical mapping (timbre, harmonics, rhythm) | Must-have |
| **Shared Memory Bridge** | `multiprocessing.shared_memory` + C++ Niagara Data Interface (NDI) | Must-have |
| **GGUF Checkpointing** | Auto-save + metadata embedding | Must-have |
| **Real-Time Dashboard HUD** | Loss curves, style switching, data injection | High |
| **Player Data Upload** | Drag-and-drop or file dialog → tokenized on-the-fly | High |
| **Hot-Swap Models** | Load previous GGUF and continue training | Medium |
| **Bio-reactive Input** | Future: MindCube / sensor streams | Stretch |

---

## 4. Visual & Audio Style

- **Visual:** UE5 PCG-driven procedural cosmos (embeddings → density fields, attention → spline paths, gradients → vector volumes) with Niagara VFX overlays powered by the same UNiagaraDataInterface.. Clean sci-fi/ambient aesthetic — dark nebulae, glowing particle clusters, attention “ribbons”, gradient “storms”.
- **Audio:** Generative ambient soundscape (additive/subtractive synthesis). Changes dynamically with training state (low loss = pure resonant tones; high entropy = chaotic pulses).
- **Mood:** Calm, meditative, awe-inspiring — think *No Man’s Sky* meets *Everything* meets a live neural visualization.

> Note: Much like style modes (light, dark, system), the UI will have the same, with an additional "Cyberpunk" style. User interfaces will also be interchangeable via the GameFeatures Plugin.

---

## 5. Technical Architecture (High-Level)

- **Python 3.14 Training Core** (separate process): Training loop + FlexAttention `score_mod` telemetry + sonification sub-interpreter.
- **Shared Memory IPC**: `multiprocessing.shared_memory` → zero-copy to UE5.
- **Unreal Engine 5.7.4**: Niagara Data Interface (C++) + HUD + main game loop.
- **Runtime Requirements**: RTX 3080+ recommended, NVIDIA drivers, Python 3.14 venv (no full CUDA Toolkit shipped).

---

## 6. Development Roadmap (Agile/Waterfall Hybrid)

We’ll use **2-week sprints** (Agile) with clear **milestones** (Waterfall-style gates). Every phase ends with a playable build + retrospective.

### **Phase 0: Environment Lock (Done – April 26, 2026)**

- UE5.7.4 source-built with Python 3.14 embedded ✅
- Versai Python venv + PyTorch 2.11 + cu130 ✅
- Rider / VS Code configured ✅

**Milestone 0:** “Python Bridge Ready”

### **Phase 1: MVP Training Core (2 weeks – Target: May 10, 2026)**

**Kanban Epics / Tasks:**

- [x] Create full `Versai/` Python package structure (`core.py`, `config.py`, `sonification.py`, `gguf_writer.py`)
- [x] Implement sample training method (CausalLM)
- [x] FlexAttention telemetry via `score_mod`
- [x] `multiprocessing.shared_memory` buffer with loss/embed/attention metrics
- [x] Basic GGUF auto-save + metadata
- [x] Simple command-line launch + live loss printing

**Milestone 1:** “Training Core Alive” – Run standalone, prints metrics, saves GGUF.

### **Phase 2: UE5 Visualization Bridge (2–3 weeks – Target: May 31, 2026)**

- [ ] C++ Niagara Data Interface (`UNiagaraDataInterfaceAmbience`)
- [ ] Map shared memory → Niagara particles/ribbons/vector fields
- [ ] Real-time HUD (loss graph, style selector, data injector)
- [ ] Basic universe visuals (point cloud + attention ribbons)
- [ ] PCG universe + Niagara VFX visualized from Playground data via NDI

**Milestone 2:** “Universe Visualized” – Training loop drives Niagara in-editor.

### **Phase 3: Sonification Engine (1–2 weeks – Target: June 14, 2026)**

- [ ] WASAPI Exclusive Mode audio thread (sub-interpreter)
- [ ] Full hierarchical mapping (embedding timbre, attention harmonics, etc.)
- [ ] Sync audio pulses with Niagara particles

**Milestone 3:** “Living Ambience” – Full audio-visual feedback loop.

### **Phase 4: Polish & Player Tools (2 weeks – Target: June 28, 2026)**

- [ ] Drag-and-drop data upload + tokenizer integration
- [ ] Style switching mid-training
- [ ] GGUF metadata + hot-swap
- [ ] Performance tuning (VRAM, 60 FPS target)
- [ ] Basic menu / onboarding flow

**Milestone 4:** “MVP Shippable” – Playable build: load data → train → export GGUF.

### **Phase 5: Stretch / Post-MVP (July onward)**

- [ ] Bio-reactive inputs
- [ ] Multi-model universe merging
- [ ] Export to Ollama / llama.cpp direct integration
- [ ] Packaging (PyInstaller launcher for players)

---

## 7. Tools & Tech Stack (Locked)

- **Engine**: Unreal Engine 5.7.4 (source)
- **ML**: Python 3.14 + PyTorch 2.11 + cu130 + FlexAttention
- **Bridge**: `multiprocessing.shared_memory` + custom C++ NDI
- **Audio**: UE5 MetaSounds
- **Model Export**: gguf-py
- **IDE**: Rider (C++) + Visual Studio Code (Python)
- **Task Tracking**: GitHub Projects or Notion Kanban (we’ll create one after this doc)

---

## 8. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|----------|
| Shared memory latency / desync | Medium | Zero-copy + profiling from day 1 |
| VRAM exhaustion on RTX 3080 | Medium | Tiny models + LoRA + gradient checkpointing |
| Python–UE5 version drift | Low | Environment variables + locked venv |
| Rider indexer pain | High | VS Code fallback + `pyproject.toml` |
| Audio glitches (WASAPI) | Medium | Sub-interpreter + incremental GC |

---

**This GDD is a living document.**  

We will update it at the end of every sprint. All tasks above are written as ready-to-drop Kanban cards.
