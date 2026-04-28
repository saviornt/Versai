# Versai (Active Development)

Procedural vibe game where real ML training is the gameplay.

Versai turns model training into an interactive environment called **The Verse**.  
Python runs training and telemetry reduction, Unreal Engine 5.7 renders and reacts through a shared-memory bridge and a custom Niagara Data Interface (NDI), and checkpoints export to GGUF.

---

## Current Project State

This repository is in active MVP/Beta development.

- MVP direction is locked (see `AGENTS.md`).
- Local alpha testing has passed.
- Next target is Steam Early Access beta.

---

## MVP Scope (Locked)

Shipped MVP/Beta scope:

- One built-in model: `CausalLM`
- One official Verse theme: `Cosmic Verse`
- One official audio theme
- Three HUD/UI packs: `Light`, `Dark`, `System`

Anything beyond this baseline (marketplace, DLC ecosystem, additional built-in model/theme packs) is post-MVP.

---

## What Is Implemented In Code Today

Verified in this repo:

- Python training entrypoint: `Python/Versai/core.py`
- Active plugin-driven trainer path: `Plugins/GameFeatures/CausalLM/Python/trainer.py`
- Structured shared-memory buffer: `Python/Versai/structured_buffer.py`
- Legacy scalar telemetry buffer (transition path): `Python/Versai/shared_memory.py`
- UE SharedMemory plugin + custom NDI:
  - `Plugins/SharedMemory/Source/Public/UNiagaraDataInterfaceVersai.h`
  - `Plugins/SharedMemory/Source/Private/UNiagaraDataInterfaceVersai.cpp`
  - `Plugins/SharedMemory/Source/Public/VizStructs.h`
- GGUF save/load helpers: `Python/Versai/gguf_fileops.py`

Current implementation note:

- Training mode is implemented.
- Inference mode is scaffolded but not fully implemented in `core.py`.

---

## Architecture Summary

```text
Python Training (CausalLM)
  -> reduction to structured telemetry
  -> shared memory (double-buffered)
  -> UNiagaraDataInterfaceVersai
  -> UE runtime systems (PCG, Niagara, MetaSounds)
```

Key constraints:

- Python shared memory is the source of truth.
- NDI is the runtime bridge.
- No raw tensor transfer to UE in hot path.
- Frame-based synchronization (`FrameId`, ready flags, monotonic consumption).

---

## Repository Layout

```text
Versai/
├── AGENTS.md
├── README.md
├── docs/
├── Python/
├── Plugins/
├── Source/
├── Config/
└── Versai.uproject
```

---

## Quick Start

Prerequisites:

- Windows 11
- Unreal Engine 5.7.4
- Python 3.14
- NVIDIA GPU recommended (RTX 3080-class target)

Setup:

1. Create Python environment and install deps:
   - `cd Python`
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
   - `pip install -e .`
2. Start training:
   - `python -m Versai.core --plugin CausalLM --mode train`
3. Open `Versai.uproject` in UE5.7.4 and connect runtime visualization flow.

---

## Documentation Map

Primary docs for implementation and planning:

- `AGENTS.md` (execution guardrails and scope boundaries)
- `docs/Versai UI-UX Design Guide.md`
- `docs/NDI-Based Design.md`
- `docs/Architecture_Design_Document.md`
- `docs/SharedMemory_StructuredBuffer_Design.md`
- `docs/Python_Playground_API.md`
- `docs/Development_Workflow.md`
- `docs/Game_Design_Document.md`
- `docs/UE5_Optimization_Guide.md`

Post-MVP:

- `docs/Models_DLC.md`

Historical context:

- `docs/GameDevPlan_Versai.md`

---

## Alignment Note

`README.md` and `AGENTS.md` are intended to stay aligned.  
If scope, architecture, or release boundaries change, update both in the same change set.

