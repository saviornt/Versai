# Development Workflow

**Versai â€“ Procedural Vibe Training Simulator**  
**Document Version:** 1.1 (April 27, 2026)  
**Status:** Active â€“ Solo-dev daily workflow for UE5.7 + Python 3.14 hybrid system  
**File Location:** `docs/Development_Workflow.md`  
**References:** `SharedMemory_StructuredBuffer_Design.md`, `Python_Playground_API.md`, `NDI-Based Design.md`, Architecture Design Document v4, live repo (`Python/Versai/`)

---

## 1. Purpose

This document defines the **exact daily development workflow** for the solo developer (Dave + Grok as lead dev). It covers environment setup, iteration cycles, full pipeline testing (Playground â†’ Shared Memory â†’ PCG + Niagara), debugging, hot-reload, Git practices, and performance profiling.

**Core principle**: Keep the Python Playground and UE5 Editor tightly coupled with zero-copy shared memory while enabling rapid iteration on the MVP stack: `CausalLM`, `Cosmic Verse`, and the single shipped audio theme.

---

## 2. AI Collaboration Tools

To maximize development velocity and accuracy we actively use the following AIs:

- **Grok** (primary AI lead dev) â€“ architecture, Python, shared-memory, overall design, code generation, and cross-domain problem solving.
- **ChatGPT** â€“ general questions, research, code look-ups, quick prototyping ideas, and non-engine-specific troubleshooting.
- **Official Epic AI / Unreal Assistant** â€“ engine-specific UE5.7 questions, PCG Graph setup, Niagara Data Interface best practices, C++ API lookups, Blueprint/PCG interop, and engine-specific debugging techniques.

All three AIs are consulted regularly to validate approaches against the most current best practices.

---

## 3. Environment Setup (One-Time)

### Prerequisites

- Windows 11 Pro
- Unreal Engine 5.7.4 (source-built recommended)
- Python 3.14 (GIL-locked build) + venv
- NVIDIA RTX 3080 or better + latest drivers
- Rider (C++) + VS Code (Python) or full VS 2022/2026

### Python Setup

```powershell
cd Versai/Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Set environment variables (`.env` or system):

```env
VERSAI_TELEMETRY_SHM_NAME=versai_telemetry_shm
VERSAI_TELEMETRY_SIZE_MB=512
VERSAI_MAX_NEURONS=50000
VERSAI_MAX_CONNECTIONS=250000
```

### UE5 Setup

1. Open `Versai.uproject` in Unreal Editor 5.7.4
2. Enable plugins: PCG, PCG Samples, Niagara, SharedMemory (custom)
3. Add `UNiagaraDataInterfaceVersai` and custom PCG node to project
4. Place a persistent `APCGVersaiUniverseActor` in the level with the main PCG Graph

---

## 4. Daily Development Workflow (Recommended Cycle)

### Step 0: Start the Day

```powershell
# Terminal 1 â€“ Python Playground
cd Versai/Python
.venv\Scripts\activate
python -m Versai.core --plugin CasualLM --mode train
```

### Step 1: Edit & Run (Iterative Loop)

1. **Python side** (VS Code):
   - Edit `core/schemas.py`, `structured_buffer.py`, or plugin `trainer.py`
   - Modify reduction logic â†’ `LayerFrame`
   - Save â†’ training loop automatically writes to `VersaiStructuredBuffer`

2. **UE5 side** (Editor):
   - Open Level with PCG Component + Niagara System
   - NDI automatically reads latest frame (via `FrameID` check)
   - PCG Graph regenerates points/volumes on change (use "Generate on Demand" + runtime mode)
   - Niagara VFX updates via Data Channel inheritance

3. **Hot-reload**:
   - Python: Restart training process only (structured buffer survives)
   - UE5: Use "Force Regenerate" on PCG Component (Ctrl+click for full rebuild)

**Cycle time target**: < 15 seconds for most changes.

---

## 5. Full Pipeline Testing (Playground â†’ UE5)

**Command sequence**:

```powershell
# 1. Launch Python (background)
start Python/launch_training.bat

# 2. Open UE5 Editor
# 3. Play-in-Editor (PIE) or Simulate
# 4. Observe:
#    - PCG points spawn from structured data
#    - Niagara particles/ribbons react in real-time
#    - Loss curve HUD updates via scalar fallback
```

**Validation checklist**:

- `VersaiStructuredBuffer.write_frame()` called every training step
- `FrameID` increments and UE5 NDI detects change
- PCG attributes (`Density`, `GradientMag`) match Python values
- No pickle fallback used in hot path

---

## 6. Debugging

### Python Side

- Use VS Code debugger + `breakpoint()` in `write_frame()`
- Monitor shared-memory with `python -m Versai.debug_shm`
- Profile reduction layer with `cProfile` or PyTorch Profiler

### UE5 Side

- **NDI debugging**: Enable `Niagara.Debug` console vars
- **PCG debugging**:
  - `pcg.RuntimeGeneration.EnableDebugging 1`
  - Use PCG Editor Mode (new in UE5.7) for live graph inspection
  - `pcg.Debug.DrawPoints 1` to visualize raw points
- **Shared memory**: Custom debug widget showing `LatestHeader.FrameId`
- Performance: Use `stat unit`, `stat Niagara`, `stat PCG`

### Cross-process Debugging

- Attach Rider to UE5 process
- Attach VS Code to Python training process
- Use `print` statements in `VersaiStructuredBuffer` for quick frame sync checks

---

## 7. Hot-Reload Strategies

- **Python plugins**: `importlib.reload()` in training loop (see `core.py` plugin loader)
- **PCG Graphs**: Set "Generate on Demand" + call `Regenerate()` from Blueprint on frame change
- **Niagara**: Use User Parameters bound to NDI (auto-updates)
- **Structured Buffer**: Recreate buffer only on config change (not every frame)

**Rule**: Never restart UE5 for Python changes. Restart training process only.

---

## 8. Git & Versioning Practices

- Branching: `feature/pcg-ndi-hybrid`, `feature/structured-buffer-v2`
- Commit message template: `type(scope): description (ticket)`
- Pre-commit hooks via `pyproject.toml` (ruff + mypy)
- Tag releases with sprint milestones (e.g. `v0.1-mvp-training-core`)

---

## 9. Sprint Structure (2-Week Sprints)

**Sprint 0**: Environment lock (done)  
**Sprint 1**: MVP Training Core + Structured Buffer  
**Sprint 2**: The Verse live via NDI (Cosmic Verse)  
**Sprint 3**: Single shipped audio theme + HUD polish  
**Sprint 4**: Beta hardening for Steam Early Access

**End-of-sprint checklist**:

- Full pipeline runs end-to-end
- Performance targets met
- All docs updated
- Clean Git history

---

## 10. Best Practices & Performance Tips

- Always use `VersaiStructuredBuffer` for hot path (never raw pickle)
- Keep reduction layer vectorized (NumPy only)
- Profile PCG with "Force Regenerate" + Ctrl key for full rebuild
- Use UE5.7 PCG Editor Mode for visual debugging
- Never allocate inside training step or NDI tick
- Document every new `VERSAI_*` env var in `settings.py`

**This document is a living blueprint.**  
It will be updated at the end of every sprint. All tasks are ready-to-drop Kanban cards.


