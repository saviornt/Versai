# UE5 Optimization Guide

**Versai – Procedural Vibe Training Simulator**  
**Document Version:** 1.1 (April 27, 2026)  
**Status:** Active – Comprehensive performance blueprint for UE5.7 source-built project  
**File Location:** `docs/UE5_Optimization_Guide.md`  
**References:** `PCG_Niagara_Hybrid_Design.md`, `SharedMemory_StructuredBuffer_Design.md`, `Python_Playground_API.md`, Architecture Design Document v3, live repo

---

## 1. Purpose

This guide provides **every practical optimization** for Unreal Engine 5.7 in the Versai project. It balances **maximum performance** (target 60+ FPS on RTX 3080-class hardware) with the **highest visual and auditory quality** required for our real-time procedural universe (PCG-driven cosmos + Niagara VFX + NDI-driven sonification).

**Core constraints**:

- Source-built UE5.7 (we can modify engine code)
- Heavy PCG runtime generation + Niagara
- Zero-copy shared memory via custom `UNiagaraDataInterfaceVersai`
- GIL-locked Python 3.14 external training process (now audio-free)
- Single-player, meditative experience — no multiplayer/network overhead

---

## 2. In-Engine Customization (Project Settings & Scalability)

### Project Settings → General

- **Target Hardware**: Windows 10/11, Scalability Level “Cinematic” as baseline, then tune down selectively.
- **Use Forward Shading**: Disabled (we need Lumen + Nanite).
- **Virtual Shadow Maps**: Enabled (best for dynamic PCG/Niagara shadows).

### Scalability Settings (Project Settings → Scalability)

- Use **Effect Types** + **Niagara Effect Budgets** for all Versai VFX.
- Set `r.Scalability.Quality` CVars per platform in `Scalability.ini`.

**Recommended base Scalability.ini** (add to Config/DefaultScalability.ini):

```ini
[Niagara]
r.Niagara.EffectBudget=1.0
r.Niagara.MaxCPUParticles=50000
r.Niagara.MaxGPUParticles=200000
```

---

## 3. Active Engine Plugins (Minimal Footprint)

**Enabled (required for Versai)**:

- PCG + PCG Samples + PCG FastGeo Interop
- Niagara + Niagara Extras
- SharedMemory (custom module)
- Audio (MetaSounds + Procedural Audio)

**Disabled**:

- Chaos (unless needed for physics)
- All unused marketplace plugins
- Virtual Production tools, MetaHuman, etc.

---

## 4. Rendering Pipeline Optimizations

### Nanite

- Enable on all procedural meshes.
- Key CVars (add to DefaultEngine.ini):

  ```ini
  r.Nanite.MaxPixelsPerEdge=32
  r.Nanite.Streaming.StreamingPoolSize=2048
  r.Nanite.Tessellation=0
  ```

### Lumen

- Hardware Ray Tracing path.
- CVars:

  ```ini
  r.Lumen.HardwareRayTracing=1
  r.Lumen.Quality=2
  ```

### Temporal Super Resolution (TSR)

- Default AA method.
- CVars:

  ```ini
  r.TSR.Quality=3
  r.Tonemapper.Quality=5
  r.MotionBlurQuality=4
  ```

---

## 5. PCG-Specific Optimizations

- FastGeometry Interop + hierarchical runtime generation.
- Pooling: `pcg.RuntimeGeneration.EnablePooling=1`.
- GPU Compute nodes preferred.
- Custom PCG Node for NDI point injection (keep lightweight).

---

## 6. Niagara-Specific Optimizations

- Data Channels for PCG → Niagara inheritance.
- Lightweight Emitters + Effect Budgets.
- GPU simulation for high particle counts.
- Materials: cheap additive/transparent, limit overdraw.

---

## 7. Sound Optimizations (UE5-Native Sonification via NDI)

**Architecture change (April 27, 2026)**: All sonification is now **100 % inside UE5**, driven in real-time by the same `UNiagaraDataInterfaceVersai` that feeds PCG and Niagara.

### Core Strategy

- NDI exposes rich telemetry (loss, activation, gradient_mag, attention_mean, etc.) as **User Parameters** / **Data Channel attributes**.
- MetaSounds graphs read these parameters directly to drive:
  - Timbre (embeddings → additive synthesis)
  - Harmonics (attention → resonant filters)
  - Rhythm / pulse (loss & gradient → envelope / LFO)
  - Spatialization / reverb (layer-based ambience)
- One master MetaSound asset (`MS_VersaiSonification`) bound to the NDI instance.

### Performance Optimizations

- Use **MetaSounds** exclusively (procedural, GPU-friendly, no sample loading overhead).
- Attach MetaSound to a persistent `USoundComponent` on the universe actor (single instance).
- Enable **Procedural Audio** and **Sound Concurrency** with low voice count.
- Key CVars (add to DefaultEngine.ini):

  ```ini
  au.MaxConcurrentSounds=64
  au.NumSources=32
  r.Audio.Thread=1                  ; Dedicated audio thread
  r.Audio.Quality=2
  ```

- Disable unnecessary Audio Mixer features:
  - `au.DisableReverb=1` unless needed for specific layers
  - `au.DisableSpatialization=0` (we want full 3D)
- NDI → MetaSound binding: Use `GetFloat` / `GetVector` VM functions exposed from NDI (zero-copy).

### Quality vs Performance Trade-offs

- High-quality resonant synthesis during low-loss states.
- Reduce harmonic complexity / LFO rate during high particle counts (via NDI-driven parameter scaling).
- Pool MetaSound instances if multiple layers ever become active.

**Advantage**: Perfect sync with visuals, no Python audio thread contention, full UE5 spatial audio tools available for future DLC ambience presets.

---

## 8. Source Code Optimizations (Engine Modifications)

Since we are source-built:

- Custom `UNiagaraDataInterfaceVersai` + MetaSound binding helpers.
- Minor patches to Niagara Data Channel system if needed for faster parameter updates.
- PCG FastGeo and Niagara proxy classes can be extended for Versai-specific fast paths.

---

## 9. Profiling & Debugging Tools

- `stat unit`, `stat Niagara`, `stat PCG`, `stat Audio`
- Niagara Debug CVars + MetaSound Graph debugger
- PCG Editor Mode + `pcg.Debug.DrawPoints 1`
- Insights traces with shared-memory markers

---

## 10. Versai-Specific Recommendations & Performance Targets

**Target**: 60+ FPS at 1440p/4K on RTX 3080-class with full universe + sonification active.

**Must-do checklist**:

- Structured buffer + double-buffered NDI
- PCG FastGeo + hierarchical runtime
- Niagara Data Channels + Lightweight Emitters
- UE5-native MetaSound sonification via NDI
- Tuned Nanite/Lumen/TSR + audio CVars
- Vectorized Python reduction layer

**Monitoring**: In-game HUD showing FrameID, PCG generation time, Niagara particle count, and MetaSound CPU usage.

**This document is a living blueprint.**  
It will be updated at the end of every sprint as we discover more engine-source wins.
