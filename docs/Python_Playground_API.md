# Python Playground API

**Versai - Procedural Vibe Training Simulator**  
**Document Version:** 1.1 (April 28, 2026)  
**Status:** Active - Source of truth for the Python backend  
**File Location:** `docs/Python_Playground_API.md`  
**References:** `Python/Versai/core.py`, `Python/Versai/structured_buffer.py`, `Python/Versai/gguf_fileops.py`, `Plugins/GameFeatures/CausalLM/Python/manifest.json`, `docs/SharedMemory_StructuredBuffer_Design.md`, `docs/NDI-Based Design.md`

---

## 1. Current Direction

The Playground is the `Python/Versai` package that owns:

- training orchestration
- data loading and reduction
- GGUF checkpointing
- structured shared-memory writes for The Verse runtime

The active shipped trainer is provided by the `CausalLM` Game Feature Plugin.

---

## 2. Plugin Configuration Ownership

`Plugins/GameFeatures/CausalLM/Python/manifest.json` is the authoritative source of truth for plugin-owned backend state.

It owns:

- game metadata
- GGUF export metadata defaults
- training metadata and defaults

The backend resolves the manifest once at training or plugin initialization. The resolved snapshot stays immutable for the lifetime of that run.

Player edits to `manifest.json` are valid, but they apply on the next training start or plugin reload, not during an active run.

CLI arguments remain valid for run-scoped controls only:

- mode
- max steps
- checkpoint cadence
- explicit checkpoint path

---

## 3. Live Implementation Shape

Current entry flow:

```python
def main():
    run_training = load_plugin_trainer(plugin_name)
    telemetry = VersaiStructuredBuffer()
    run_training(telemetry_buffer=telemetry, ...)
```

Current characteristics:

- plugin-driven trainer loading via `importlib`
- manifest-backed `CausalLM` config resolution
- structured shared-memory telemetry via `VersaiStructuredBuffer`
- GGUF export via `gguf_fileops.py`

Current limitation:

- the shared-memory contract still needs hardening so the UE reader and Python writer agree on exact buffer semantics and layout

---

## 4. GGUF Metadata Policy

GGUF exports should include:

- model identity
- plugin identity
- default Verse identity
- default audio theme identity
- training style identity
- manifest-backed training metadata needed for continuation or inspection

Manifest-backed metadata should be exported under explicit `versai.*` keys.

---

## 5. MVP Backend Rules

- Do not treat environment variables as the source of truth for plugin-owned metadata.
- Use `manifest.json` for plugin-owned metadata and defaults.
- Keep core runtime settings under `VERSAI_*` where they are application-level rather than plugin-level.
- Keep one authoritative telemetry write per training step.
- Keep shared-memory payloads allocation-aware and zero-copy compatible.

---

## 6. Near-Term Work

Phase 2 and Phase 3 backend work should focus on:

- exact writer/reader binary contract alignment
- manifest-backed GGUF metadata export
- stronger scalar telemetry for HUD and MetaSounds
- real dataset tokenization and collation
- deterministic restart behavior for shared memory

---

This document is a living blueprint and should be updated with any backend behavior change that affects runtime configuration, telemetry, or checkpoint semantics.
