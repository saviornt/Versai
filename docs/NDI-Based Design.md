# NDI-Based Design

**Versai - Procedural Vibe Training Simulator**  
**Document Version:** 1.0 (April 28, 2026)  
**Status:** Active - Canonical architecture for NDI-driven runtime systems  
**File Location:** `docs/NDI-Based Design.md`  
**References:** `Architecture_Design_Document.md`, `SharedMemory_StructuredBuffer_Design.md`, `Python_Playground_API.md`, `UE5_Optimization_Guide.md`, `Versai UI-UX Design Guide.md`

---

## 1. Purpose

This document defines the runtime architecture where **`UNiagaraDataInterfaceVersai` (NDI)** is the single telemetry bridge from Python training to Unreal systems.

NDI controls and synchronizes:

- **PCG** (primary world generation for **The Verse**)
- **Niagara** (secondary VFX overlays and motion language)
- **MetaSounds** (reactive sonification)

The goal is deterministic, low-latency, frame-based updates with one source of truth.

---

## 2. MVP/Beta Scope (Locked)

For MVP/Beta (Steam Early Access target), this architecture ships with:

- One model: `CausalLM`
- One Verse theme: `Cosmic Verse`
- One audio theme (MetaSound graph)
- Three HUD/UI packs: `Light`, `Dark`, `System`

Plugin marketplace and multi-model DLC systems are post-MVP.

---

## 3. Design Principles

1. **Single Source of Truth**: Python shared memory is authoritative.
2. **Single Runtime Bridge**: NDI is the only gameplay-facing ingestion path.
3. **Frame-Based Determinism**: UE systems consume `FrameId`-ordered snapshots.
4. **Zero-Allocation Hot Path**: No per-frame heap allocations in Python writer, NDI read, or core update path.
5. **One Data, Three Consumers**: Same telemetry frame drives PCG, Niagara, and MetaSounds.

---

## 4. Data Path

```text
Python Training (CausalLM)
  -> Reduction Layer (LayerFrame)
  -> VersaiStructuredBuffer (double-buffered shared memory)
  -> UNiagaraDataInterfaceVersai (C++ reader + exposed VM funcs/params)
  -> PCG Graph (The Verse structure)
  -> Niagara Systems (VFX behavior)
  -> MetaSounds (audio response)
```

---

## 5. NDI Responsibilities

`UNiagaraDataInterfaceVersai` is responsible for:

- Reading latest valid `FrameHeader` (`ready`, `frame_id > last_frame`).
- Mapping shared-memory structs to UE-native read views.
- Exposing VM functions/user parameters for:
  - scalar telemetry (`loss`, `attention_mean`, `stability`)
  - per-point attributes (`activation`, `density`, `gradient_mag`)
  - connection attributes (`weight`, `thickness`)
- Publishing synchronized values to PCG/Niagara/MetaSounds each frame.
- Handling safe fallback when no fresh frame is available.

NDI must not perform training logic, serialization, or dynamic schema mutation at runtime.

---

## 6. PCG Integration (The Verse)

PCG is the structural layer of The Verse.

MVP mapping:

- `position` -> point location in Cosmic Verse
- `density` -> local cluster fullness
- `activation` -> emissive bias / structural intensity
- `gradient_mag` -> turbulence / instability zones

Runtime behavior:

- Consume latest NDI-fed attributes.
- Regenerate only when `FrameId` changes.
- Prefer pooled/runtime-generation-safe nodes.

---

## 7. Niagara Integration

Niagara is the motion and effect layer, not the structural authority.

MVP mapping:

- `attention_mean` -> ribbon coherence
- `weight` / `thickness` -> connective strand profile
- `loss` -> global atmosphere intensity
- `gradient_mag` -> storm-like local effects

Rules:

- GPU sim preferred for high counts.
- Use effect budgets and capped emitter counts.
- Keep materials lightweight to avoid overdraw spikes.

---

## 8. MetaSounds Integration (Single Shipped Theme)

MetaSounds consumes the same NDI frame used by visuals.

MVP mapping:

- `loss` -> macro tension/release
- `attention_mean` -> harmonic spread
- `activation variance` -> timbral density
- `stability` -> rhythmic regularity

Implementation notes:

- One persistent MetaSound instance bound to universe actor.
- Parameter updates are frame-synced via NDI-exposed values.
- Avoid per-frame graph rebuilds or dynamic asset swaps.

---

## 9. Runtime Update Order

Per UE frame:

1. NDI reads latest completed frame.
2. Frame validity check (`ready`, monotonic `FrameId`).
3. Cache/update NDI parameter set.
4. PCG consumes structural attributes.
5. Niagara consumes effect attributes.
6. MetaSounds consumes audio attributes.
7. Debug overlay updates (`FrameId`, counts, timings).

---

## 10. Performance Targets

- Python write: `< 1.0 ms/frame`
- NDI read + map: `< 0.5 ms/frame`
- PCG update budget: `< 2.0 ms/frame` average
- Niagara update budget: GPU-bound with stable 60 FPS target
- MetaSound CPU budget: low single-digit ms

Primary hardware target: RTX 3080-class system at 1440p.

---

## 11. Validation Checklist

- `FrameId` increments continuously during training.
- No stale-frame replay when writer is active.
- PCG, Niagara, and MetaSounds respond to the same frame transition.
- No dynamic allocations in hot path (profiling confirmed).
- Fallback behavior works when training pauses/stops.

---

## 12. Post-MVP Extensions

- Additional Verse themes via Game Feature Plugins.
- Additional audio theme packs.
- Model DLC + marketplace integration.
- Multi-model blending and cross-verse transitions.

These extensions must continue to use NDI as the shared runtime bridge.
