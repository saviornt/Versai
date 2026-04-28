# Engineering Neural Ambience: A Technical Framework for Real-Time Neural Network Training and Procedural Universe Synthesis

## Current Use Note (April 28, 2026)

This file is retained as **historical context**.  
For active implementation and RAG grounding, prioritize:

- `docs/Architecture_Design_Document.md`
- `docs/NDI-Based Design.md`
- `docs/Game_Design_Document.md`
- `docs/Versai UI-UX Design Guide.md`

## ⚠️ HISTORICAL TECHNICAL FRAMEWORK (April 26, 2026)

This document reflects the pre-hybrid vision.  
Current architecture (v4): Shared Memory → UNiagaraDataInterface → (PCG Graphs + Niagara VFX).
See Architecture Design Document_v4.md for the live spec.

---

The convergence of high-performance deep learning and real-time interactive environments has catalyzed a new paradigm in software engineering: the development of 'ambience' games that serve as functional, visual, and auditory interfaces for live neural network training. Unlike traditional simulations where artificial intelligence is a secondary component for non-player character behavior, the proposed project positions the training of a large-scale neural model as the primary mechanical engine of the experience. This report details the architectural requirements, implementation strategies, and theoretical foundations for constructing such a system on a Windows 11 Pro workstation powered by an NVIDIA RTX 3080, utilizing the bleeding-edge software stack of Python 3.14 and PyTorch 2.11.

## **Foundational Technical Environment**

The selection of the software stack is governed by the need for extreme concurrency and low-latency data throughput. Python 3.14 represents a landmark release in the language's history, primarily due to the stabilization of free-threaded execution and the experimental JIT compiler.1 For a neural training environment that must simultaneously manage a 3D rendering pipeline and a generative audio system, the removal of the Global Interpreter Lock (GIL) is not merely an optimization but a structural necessity.2

### **Hardware and Driver Synchronization**

The NVIDIA RTX 3080, based on the Ampere architecture (SM 8.6), provides the necessary Tensor Cores to handle the computational intensity of PyTorch 2.11. While PyTorch 2.11 introduces specialized backends for newer architectures like Blackwell and Hopper, the Ampere architecture remains the baseline for high-performance consumer-grade neural rendering.3 The integration of CUDA 13 as the default version in this release ensures that the system can leverage the latest memory management features and kernel optimizations provided by NVIDIA.5

| Component | Version/Specification | Strategic Role |
| :---- | :---- | :---- |
| Operating System | Windows 11 Pro | Host for WASAPI low-latency audio and NVIDIA drivers 7 |
| CPU Runtime | Python 3.14 (Free-Threaded) | Parallel management of training, IPC, and audio threads 1 |
| Deep Learning | PyTorch 2.11cu130 | Tensor core acceleration and FlexAttention API 5 |
| CUDA Toolkit | CUDA 13.0 | Foundation for high-performance GPU kernels 3 |
| GPU Architecture | NVIDIA RTX 3080 (Ampere) | Target for SM 8.6 optimized tensor operations 3 |
| Rendering Engine | Unreal Engine 5.5+ | Procedural "Universe" visualization via Niagara 9 |

The transition to CUDA 13 involves significant changes in binary support, specifically the removal of legacy architectures like Volta, which allows the PyTorch team to optimize the toolchain for modern GPUs.11 For the RTX 3080, this translates to improved throughput in scaled dot-product attention (SDPA) and better integration with the Windows-based display driver model.3

## **Architectural Synthesis of the Neural Engine**

The 'ambience' game architecture is divided into three primary domains: the Training Core, the Visualization Bridge, and the Sonification Engine. Each domain operates in a distinct thread or process, synchronized through high-performance shared memory protocols to ensure that the visual and auditory feedback is a real-time reflection of the network's internal state.

### **Python 3.14 and Multi-Interpreter Isolation**

The implementation utilizes PEP 734, which introduces the concurrent.interpreters module, allowing the management of multiple isolated Python interpreters within a single process.14 This is critical for the ambience game, as it allows the training loop—which is often prone to memory fragmentation and jitter—to run in a separate interpreter from the audio synthesis and dashboard UI. This isolation ensures that even under heavy computational load, the audio thread maintains its strict periodicity, preventing glitches.7

### **PyTorch 2.11 and the FlexAttention Paradigm**

At the heart of the training core is the FlexAttention API, introduced as a prototype and expanded in PyTorch 2.11.5 FlexAttention allows the developer to define custom attention variants using Python functions that are then JIT-compiled into high-performance Triton or FlashAttention-4 kernels.16 In a traditional game engine, accessing attention weights in real-time requires expensive hooks or custom C++ extensions. With FlexAttention, the game's visualization engine can inject "telemetry mods" directly into the attention calculation.

![][image1]

The score\_mod function serves as the primary data extraction point. By passing a callable that writes to a shared memory buffer, the training loop can broadcast the attention patterns of every head to the visualization and sonification engines without interrupting the forward pass.8

## **The Procedural Universe: Visualization Strategy**

The visual component of the project is defined as a 'universe-creation' simulation. This is not a static rendering but a procedural manifestation of the neural network's weights, gradients, and activation patterns.

### **Niagara Data Interfaces and C++ Synchronization**

To achieve real-time 3D visualization of the embedding space and attention heads, the project utilizes Unreal Engine 5's Niagara VFX system.9 However, because the training logic resides in a separate Python interpreter, a high-speed bridge is required. The most effective method is a custom Niagara Data Interface (NDI) implemented in C++.18

The NDI functions by mapping a shared memory region, created in Python via the mmap module or the ZeroIPC library, directly into the GPU's memory space.19 The RTX 3080’s support for unified memory and high-bandwidth PCIe 4.0 allows the Niagara system to treat the model's weight tensors as a dynamic particle source.10 Each particle in the 'universe' represents a token in the latent space, with its position, color, and velocity determined by its embedding vector and the current gradient flow.4

### **Neural Rendering and Procedural Geometry**

The visualization adopts techniques from 'Neural Rendering', where neural networks are used to reshape 3D rendering pipelines.4 Instead of traditional rasterization, the game uses triangle tokens—encoding spatial position, surface normal, and physical properties—to represent the evolving model.4 As the network trains, the "universe" undergoes topological shifts; well-clustered embeddings form stars or galaxies, while high-loss states manifest as chaotic nebulas.

| Visualization Layer | Neural Source | Rendering Technique |
| :---- | :---- | :---- |
| Embedding Manifold | ![][image2] Weights | 3D Point Cloud via Niagara 10 |
| Attention Flux | ![][image3] Dot Products | Ribbon Emitters and Volumetric Fog 9 |
| Latent Transitions | Hidden Layer Activations | Procedural Mesh Displacement 23 |
| Gradient Storms | ![][image4] Values | GPU-accelerated Vector Fields 24 |

The use of real-time tessellation allows the game to progressively refine the accuracy of the resulting geometry based on the player's proximity to a specific cluster of data, ensuring that the 10GB of VRAM on the RTX 3080 is utilized efficiently.23

## **The Sonification Engine: Mapping Neural Dynamics to Sound**

A core requirement of the ambience game is a complex audio sonification system. This system must translate the abstract mathematical operations of the transformer into a generative ambient soundscape that is both aesthetically pleasing and informative of the training progress.25

### **Synthesis Mapping Hierarchy**

The sonification engine utilizes a hierarchical mapping strategy, where different components of the neural architecture are assigned to specific parameters of an additive and subtractive synthesis model.26

1. **Embedding Space (Timbre)**: The magnitude and variance of the embedding vectors are mapped to the timbral density of the sound. High-variance embeddings produce complex, rich spectra, while a converged, low-variance space results in pure, resonant tones.26  
2. **Attention Mechanisms (Harmonic Structure)**: The ![][image3] overlap is mapped to the harmonic series. As different attention heads "attend" to specific tokens, the sonification engine triggers resonant filters at specific frequencies corresponding to those tokens.17  
3. **Token Prediction (Rhythm and Pulse)**: The softmax output of the final layer controls the rhythmic regularity of the environment. High-entropy predictions (uncertainty) create stochastically distributed audio pulses, while high-confidence predictions align these pulses into a steady beat.28  
4. **Training Dynamics (Space and Texture)**: The loss curve and gradient magnitude are mapped to the spatialization (reverb and delay) and the "roughness" (distortion) of the soundscape. An accelerating training pace creates a sense of forward motion through doppler effects.29

### **Low-Latency Implementation on Windows**

To ensure the audio responds in real-time to the training loop, the system must bypass the standard Windows audio mixer. Using the SoundCard library, the Python Sonification Engine opens a WASAPI Exclusive Mode stream.7 This reduces the round-trip latency to below 10ms, which is the threshold required for the audio to feel "connected" to the visual transitions in the Niagara universe.31

Python 3.14’s incremental garbage collector is vital in this context. Traditional Python garbage collection can cause "stop-the-world" pauses of 50-100ms, which would result in audible pops or clicks in the stream.1 The incremental approach in version 3.14 processes the "young" and "old" generations in smaller chunks, maintaining the real-time integrity of the audio buffer.1

## **GGUF Model Management and Checkpointing**

As the user "sculpts" the neural network through the ambience game, the system must provide robust mechanisms for saving and exporting the resulting artifacts. The GGUF format (GGML Universal File) is selected as the primary output format due to its efficiency in local inference and its support for extensive metadata.32

### **Programmatic GGUF Generation**

The game includes a background thread dedicated to the GGUF pipeline. This thread monitors the training progress and performs auto-saving based on a "stability threshold"—a combination of loss plateauing and embedding clustering.33 When a checkpoint is triggered, the system uses the gguf-py library to write the model weights directly to a binary file.35

One unique feature of this project is the embedding of "Ambience Metadata" into the GGUF file. This includes the training style selected by the user, the dataset used, and even a signature of the sonification settings at the time of the save.33

| Key Feature | GGUF Advantage | Implementation in Project |
| :---- | :---- | :---- |
| Fast Loading | Binary format with header metadata | Rapid hot-swapping of models in-game 32 |
| Quantization | Support for Q4\_K\_M, Q8\_0, etc. | Automatic compression for low-RAM devices 37 |
| Interoperability | Use with llama.cpp or Ollama | Exporting models for external use 32 |
| Single File | Weights and metadata in one artifact | Simplified checkpoint management 40 |

The auto-save system utilizes the new compression.zstd module in Python 3.14 to compress non-weight metadata, ensuring that checkpoint files remain manageable on the user’s disk.1

## **Training Styles and Dataset Orchestration**

The user interface of the ambience game provides a "Real-Time Dashboard" for the selection and configuration of training paradigms and data sources. This dashboard is implemented as a semi-transparent HUD within the 3D environment, communicating with the training core via a dedicated IPC channel.41

### **Training Style Selection**

The game offers several 'styles' of neural training, each resulting in a different visual and auditory signature:

* **Self-Supervised Fluency**: A standard causal language modeling objective. This style is characterized by a "spiral" universe formation as the model learns to predict the next token in a sequence.43  
* **Adversarial Style Transfer**: Utilizing a discriminator to impart a specific aesthetic style onto the generated weights. This is visualized as two competing "galaxies" where the boundary between them represents the discriminator's gradient.45  
* **Reinforcement Exploration**: An agent-based training style where the network learns through interaction. The visualization focuses on "trajectories" and "reward fields," with audio feedback corresponding to successful explorations.43

### **Dataset Integration**

The project supports the dynamic loading of various datasets, which act as the "raw materials" for the universe-creation process. The dataset selection influences the initial state of the embedding space.

1. **Textual Corpora**: Mapped using a custom Tokenizers-UE5 plugin, allowing the engine to visualize the semantic relationship between words in real-time.47  
2. **Protein Sequences**: Leveraging bioinformatics libraries to translate amino acid sequences into structural representations, influencing the "physical laws" of the procedural universe.26  
3. **Sensor Data Streams**: Real-time inputs from external devices (e.g., the MindCube) can be injected into the training loop, creating a bio-reactive ambience.29

## **Technical Implementation Plan and Scaffolding**

The following section provides the code scaffolding and architectural logic for the core components of the project. This is designed to be built within a C++ Unreal Engine project using a Python 3.14 environment.

### **Code Scaffolding: The Training Orchestrator**

Python

\# Environment: Python 3.14 with Free-Threading Enabled  
\# Dependencies: torch==2.11.0, gguf, numpy, soundcard

import torch  
import torch.nn as nn  
from torch.nn.attention.flex\_attention import flex\_attention  
import shared\_memory\_ipc \# Custom library using ZeroIPC or mmap  
import audio\_engine \# Custom WASAPI wrapper

class AmbienceTransformer(nn.Module):  
    def \_\_init\_\_(self, vocab\_size, d\_model, n\_heads):  
        super().\_\_init\_\_()  
        self.embeddings \= nn.Embedding(vocab\_size, d\_model)  
        self.heads \= n\_heads  
          
    def forward(self, x, telemetry\_buffer):  
        \# score\_mod captures data for sonification and visualization  
        def telemetry\_mod(score, b, h, q\_idx, kv\_idx):  
            \# Write attention scores to shared memory for the NDI  
            telemetry\_buffer.write\_attention(score, h, q\_idx, kv\_idx)  
            return score

        \# Utilizing PyTorch 2.11 FlexAttention  
        \# This is JIT compiled for the RTX 3080  
        x \= self.embeddings(x)  
        \# Simplified for scaffolding  
        q, k, v \= self.project(x)  
        attn\_output \= flex\_attention(q, k, v, score\_mod=telemetry\_mod)  
        return attn\_output

def training\_loop(config):  
    \# Enable Python 3.14 JIT  
    import os  
    os.environ \= "1"  
      
    device \= "cuda" if torch.cuda.is\_available() else "cpu"  
    model \= AmbienceTransformer(config.vocab, config.dim, config.heads).to(device)  
    optimizer \= torch.optim.AdamW(model.parameters(), lr=config.lr)  
      
    \# Initialize Shared Memory for UE5 Niagara and Audio  
    ipc \= shared\_memory\_ipc.create\_buffer(size=1024 \* 1024 \* 100) \# 100MB  
      
    while True:  
        data \= config.dataset.next\_batch()  
        output \= model(data, ipc)  
        loss \= compute\_loss(output, target)  
        loss.backward()  
          
        \# Update shared memory with gradients and embeddings for sonification  
        ipc.update\_metrics(loss.item(), model.embeddings.weight.grad)  
          
        optimizer.step()  
        optimizer.zero\_grad()  
          
        \# Auto-save Checkpoint in GGUF format  
        if epoch\_completed:  
            save\_to\_gguf(model, "checkpoints/latest.gguf", config.metadata)

### **Code Scaffolding: The Niagara Data Interface (UE5 C++)**

C++

// NDI\_Ambience.h  
\#**pragma** once  
\#**include** "NiagaraDataInterface.h"  
\#**include** "NDI\_Ambience.generated.h"

UCLASS(EditInlineNew, Category \= "NeuralAmbience")  
class UNiagaraDataInterfaceAmbience : public UNiagaraDataInterface  
{  
    GENERATED\_UCLASS\_BODY()

public:  
    // Shared Memory handle for the PyTorch buffers  
    void\* SharedBufferPointer;

    // Functions exposed to Niagara Graph  
    virtual void GetFunctions(TArray\<FNiagaraFunctionSignature\>& OutFunctions) override;  
    virtual void GetVMExternalFunction(const FNiagaraFunctionSignature& Sig, FString& OutHLSL,...) override;

    // Called every frame to sync the buffer from PyTorch  
    void Tick(float DeltaTime) {  
        // Direct memory access to the shared buffer populated by Python 3.14  
        // Update GPU-side buffers for Niagara emitters  
    }  
};

## **Detailed Architectural Plan**

The execution of this project requires a deep synchronization between the host operating system's resources and the GPU's compute capabilities.

### **Multi-Process Synchronization and Shared Memory**

Given the complexity of the training loop and the rendering engine, the architecture adopts a producer-consumer model using shared memory. The Python process acts as the **Producer**, managing the neural weights and calculating the attention scores. Unreal Engine 5 acts as the **Consumer**, reading these weights to drive the Niagara particles.20

The ZeroIPC approach is particularly relevant here. By treating shared memory as an "active computational substrate" rather than passive storage, the C++ Niagara interface can read the PyTorch tensors with zero-copy overhead.20 This is achieved by creating a named shared memory segment in Windows 11 (CreateFileMapping and MapViewOfFile), which both the Python mmap module and the UE5 C++ plugin can access simultaneously.49

### **Sonification Logic and Signal Flow**

The sonification engine operates as a separate sub-interpreter to avoid GIL contention.14 The signal flow is as follows:

1. **Telemetry Extraction**: The training loop writes the current attention entropy and loss delta to a circular buffer in shared memory.  
2. **Parameter Mapping**: The audio interpreter reads this buffer at 44.1kHz or 48kHz. It maps the attention entropy to the cutoff frequency of a resonant low-pass filter.26  
3. **Synthesis**: Using the SoundCard library, it generates a raw PCM buffer. For the RTX 3080 system, the synthesis is often performed using NumPy arrays, which are blitted to the audio driver via WASAPI.15  
4. **Feedback Loop**: The "sonic state" is then written back to the shared memory, allowing the Niagara particles to "pulse" in sync with the audio.29

### **Windows 11 Pro System Optimization**

To maintain the performance of this complex ecosystem, specific OS-level configurations are required. Windows 11 Pro's "High Performance" power plan must be active to prevent CPU throttling, which is the primary cause of latency spikes in real-time audio.52 Additionally, the RTX 3080's "Hardware-Accelerated GPU Scheduling" (HAGS) should be enabled to improve the responsiveness of the Niagara visualization during high training loads.

The use of the compression.zstd module in Python 3.14 is leveraged for fast decompression of training data as it is moved from the NVMe storage to the training core, reducing the bottleneck of data loading.1

## **Conclusion: The Future of Neural Ambience**

The development of a neural-training-as-game-engine project represents a significant step toward making artificial intelligence more interpretable and aesthetically tangible. By building on the foundations of Python 3.14 and PyTorch 2.11, and leveraging the immense power of the RTX 3080 under CUDA 13, this project demonstrates that neural network training is no longer a background batch process but a dynamic, immersive experience. The combination of Niagara's procedural universe, the complex sonification of the latent space, and the standardized GGUF checkpointing pipeline provides a comprehensive blueprint for the next generation of intelligent creative tools. This architectural plan ensures that the "Neural Ambience" is not just a visual spectacle but a robust environment for real-world AI development and exploration.

#### **Works cited**

1. Python 3.14 Features \- Kaggle, accessed April 25, 2026, [https://www.kaggle.com/discussions/general/611848](https://www.kaggle.com/discussions/general/611848)  
2. Python 3.14: The present and future of the language of the moment \- ALTIA, accessed April 25, 2026, [https://www.altiacompany.com/en/insights/blog/python-314-present-and-future-language-moment](https://www.altiacompany.com/en/insights/blog/python-314-present-and-future-language-moment)  
3. pytorch/RELEASE.md at main \- GitHub, accessed April 25, 2026, [https://github.com/pytorch/pytorch/blob/main/RELEASE.md](https://github.com/pytorch/pytorch/blob/main/RELEASE.md)  
4. RenderFormer: How neural networks are reshaping 3D rendering \- Microsoft Research, accessed April 25, 2026, [https://www.microsoft.com/en-us/research/blog/renderformer-how-neural-networks-are-reshaping-3d-rendering/](https://www.microsoft.com/en-us/research/blog/renderformer-how-neural-networks-are-reshaping-3d-rendering/)  
5. PyTorch 2.11 Release Blog – PyTorch, accessed April 25, 2026, [https://pytorch.org/blog/pytorch-2-11-release-blog/](https://pytorch.org/blog/pytorch-2-11-release-blog/)  
6. Transitioning PyPI CUDA wheels to CUDA 13.0 as the stable (Release 2.11), accessed April 25, 2026, [https://dev-discuss.pytorch.org/t/transitioning-pypi-cuda-wheels-to-cuda-13-0-as-the-stable-release-2-11/3325](https://dev-discuss.pytorch.org/t/transitioning-pypi-cuda-wheels-to-cuda-13-0-as-the-stable-release-2-11/3325)  
7. Low Latency Audio \- Windows drivers | Microsoft Learn, accessed April 25, 2026, [https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/low-latency-audio](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/low-latency-audio)  
8. torch.nn.attention.flex\_attention — PyTorch 2.11 documentation, accessed April 25, 2026, [https://docs.pytorch.org/docs/stable/nn.attention.flex\_attention.html](https://docs.pytorch.org/docs/stable/nn.attention.flex_attention.html)  
9. Overview of Niagara Effects for Unreal Engine \- Epic Games Developers, accessed April 25, 2026, [https://dev.epicgames.com/documentation/unreal-engine/overview-of-niagara-effects-for-unreal-engine](https://dev.epicgames.com/documentation/unreal-engine/overview-of-niagara-effects-for-unreal-engine)  
10. How we wrote a GPU-based Gaussian Splats viewer in Unreal with Niagara \- Magnopus, accessed April 25, 2026, [https://www.magnopus.com/blog/how-we-wrote-a-gpu-based-gaussian-splats-viewer-in-unreal-with-niagara](https://www.magnopus.com/blog/how-we-wrote-a-gpu-based-gaussian-splats-viewer-in-unreal-with-niagara)  
11. PyTorch 2.11.0 Release \- GitHub, accessed April 25, 2026, [https://github.com/pytorch/pytorch/releases](https://github.com/pytorch/pytorch/releases)  
12. Introducing CUDA 13.2 and Deprecating CUDA 12.8 (Release 2.12), accessed April 25, 2026, [https://dev-discuss.pytorch.org/t/introducing-cuda-13-2-and-deprecating-cuda-12-8-release-2-12/3337](https://dev-discuss.pytorch.org/t/introducing-cuda-13-2-and-deprecating-cuda-12-8-release-2-12/3337)  
13. torch.nn.attention — PyTorch 2.11 documentation, accessed April 25, 2026, [https://docs.pytorch.org/docs/stable/nn.attention.html](https://docs.pytorch.org/docs/stable/nn.attention.html)  
14. Python 3.14 – What you need to know \- Cloudsmith, accessed April 25, 2026, [https://cloudsmith.com/blog/python-3-14-what-you-need-to-know](https://cloudsmith.com/blog/python-3-14-what-you-need-to-know)  
15. bastibe/SoundCard: A Pure-Python Real-Time Audio Library \- GitHub, accessed April 25, 2026, [https://github.com/bastibe/SoundCard](https://github.com/bastibe/SoundCard)  
16. FlexAttention \+ FlashAttention-4: Fast and Flexible \- PyTorch, accessed April 25, 2026, [https://pytorch.org/blog/flexattention-flashattention-4-fast-and-flexible/](https://pytorch.org/blog/flexattention-flashattention-4-fast-and-flexible/)  
17. Tracing Attention Computation Through Feature Interactions \- Transformer Circuits Thread, accessed April 25, 2026, [https://transformer-circuits.pub/2025/attention-qk/index.html](https://transformer-circuits.pub/2025/attention-qk/index.html)  
18. Niagara Data Interfaces | Epic Developer Community, accessed April 25, 2026, [https://dev.epicgames.com/community/learning/knowledge-base/jPMm/unreal-engine-niagara-data-interfaces](https://dev.epicgames.com/community/learning/knowledge-base/jPMm/unreal-engine-niagara-data-interfaces)  
19. fuzziqersoftware/sharedstructures: Dynamically-sized shared-memory data structures in C++ and Python 3 \- GitHub, accessed April 25, 2026, [https://github.com/fuzziqersoftware/sharedstructures](https://github.com/fuzziqersoftware/sharedstructures)  
20. ZeroIPC: Shared Memory as a Computational Substrate \- metafunctor, accessed April 25, 2026, [https://metafunctor.com/post/2025-01-zeroipc/](https://metafunctor.com/post/2025-01-zeroipc/)  
21. Hunyuan3D Studio: End-to-End AI Pipeline for Game-Ready 3D Asset Generation \- arXiv, accessed April 25, 2026, [https://arxiv.org/html/2509.12815v1](https://arxiv.org/html/2509.12815v1)  
22. Niagara UI Renderer | Free Plugin for UE4/UE5 \- Epic Developer Community Forums, accessed April 25, 2026, [https://forums.unrealengine.com/t/niagara-ui-renderer-free-plugin-for-ue4-ue5/211365](https://forums.unrealengine.com/t/niagara-ui-renderer-free-plugin-for-ue4-ue5/211365)  
23. (PDF) 3D MODEL VISUALIZATION ENHANCEMENTS IN REAL-TIME GAME ENGINES, accessed April 25, 2026, [https://www.researchgate.net/publication/286976381\_3D\_MODEL\_VISUALIZATION\_ENHANCEMENTS\_IN\_REAL-TIME\_GAME\_ENGINES](https://www.researchgate.net/publication/286976381_3D_MODEL_VISUALIZATION_ENHANCEMENTS_IN_REAL-TIME_GAME_ENGINES)  
24. How To Stream Niagara System Data Into Render Targets \- 80 Level, accessed April 25, 2026, [https://80.lv/articles/niagara-system-integration-with-render-targets-in-unreal-engine-5](https://80.lv/articles/niagara-system-integration-with-render-targets-in-unreal-engine-5)  
25. Project Classification Strategies in the Data Sonification Archive \- Re.Public@polimi.it, accessed April 25, 2026, [https://re.public.polimi.it/retrieve/50c54ffb-6994-48d5-b0dc-30fb0ea34f47/Re%28de%29fining\_Sonification\_\_Project\_Classification\_Strategies\_in\_the\_Data\_Sonification\_Archive\_\_doc.pdf](https://re.public.polimi.it/retrieve/50c54ffb-6994-48d5-b0dc-30fb0ea34f47/Re%28de%29fining_Sonification__Project_Classification_Strategies_in_the_Data_Sonification_Archive__doc.pdf)  
26. A Self-Consistent Sonification Method to Translate Amino Acid Sequences into Musical Compositions and Application in Protein Design Using Artificial Intelligence | ACS Nano \- ACS Publications, accessed April 25, 2026, [https://pubs.acs.org/doi/10.1021/acsnano.9b02180](https://pubs.acs.org/doi/10.1021/acsnano.9b02180)  
27. Sonification based de novo protein design using artificial intelligence, structure prediction, and analysis using molecular modeling \- PMC, accessed April 25, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7078008/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7078008/)  
28. AI Sonification for an Inclusive Data-Driven World \- IEEE Computer Society, accessed April 25, 2026, [https://www.computer.org/publications/tech-news/trends/ai-sonification](https://www.computer.org/publications/tech-news/trends/ai-sonification)  
29. Two Sonification Methods for the MindCube \- New Interfaces for Musical Expression, accessed April 25, 2026, [https://nime.org/proceedings/2025/nime2025\_74.pdf](https://nime.org/proceedings/2025/nime2025_74.pdf)  
30. DDP Communication Hooks — PyTorch 2.11 documentation, accessed April 25, 2026, [https://docs.pytorch.org/docs/stable/ddp\_comm\_hooks.html](https://docs.pytorch.org/docs/stable/ddp_comm_hooks.html)  
31. Lessons learnt building a real-time audio application in Python | Hacker News, accessed April 25, 2026, [https://news.ycombinator.com/item?id=41488805](https://news.ycombinator.com/item?id=41488805)  
32. GGUF · Hugging Face, accessed April 25, 2026, [https://huggingface.co/docs/hub/gguf](https://huggingface.co/docs/hub/gguf)  
33. Fine-Tuning GGUF Models: A Practical Guide | by Hey Amit \- Medium, accessed April 25, 2026, [https://medium.com/@heyamit10/fine-tuning-gguf-models-a-practical-guide-d4cc83f9e157](https://medium.com/@heyamit10/fine-tuning-gguf-models-a-practical-guide-d4cc83f9e157)  
34. GGUF, the long way around | Vicki Boykis, accessed April 25, 2026, [https://vickiboykis.com/2024/02/28/gguf-the-long-way-around/](https://vickiboykis.com/2024/02/28/gguf-the-long-way-around/)  
35. llama.cpp/gguf-py/README.md at master · ggml-org/llama.cpp · GitHub, accessed April 25, 2026, [https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/README.md](https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/README.md)  
36. gguf-py/README.md · b2276 · Till-Ole Herbst / Llama.Cpp \- GitLab, accessed April 25, 2026, [https://gitlab.informatik.uni-halle.de/ambcj/llama.cpp/-/blob/b2276/gguf-py/README.md](https://gitlab.informatik.uni-halle.de/ambcj/llama.cpp/-/blob/b2276/gguf-py/README.md)  
37. Convert Pytorch Model to Quantize GGUF to Run on Ollama | by Sarin Suriyakoon \- Medium, accessed April 25, 2026, [https://medium.com/palo-it-thailand/convert-pytorch-model-to-quantize-gguf-to-run-on-ollama-5c5dbc458208](https://medium.com/palo-it-thailand/convert-pytorch-model-to-quantize-gguf-to-run-on-ollama-5c5dbc458208)  
38. GGUF in Practice: From Model to Production (Part 2\) \- Medium, accessed April 25, 2026, [https://medium.com/@michael.hannecke/gguf-in-practice-from-model-to-production-part-2-27c7eed23daa](https://medium.com/@michael.hannecke/gguf-in-practice-from-model-to-production-part-2-27c7eed23daa)  
39. How do I create a GGUF model file? \- SecondState.io, accessed April 25, 2026, [https://www.secondstate.io/articles/convert-pytorch-to-gguf/](https://www.secondstate.io/articles/convert-pytorch-to-gguf/)  
40. GGUF · Hugging Face, accessed April 25, 2026, [https://huggingface.co/docs/transformers/gguf](https://huggingface.co/docs/transformers/gguf)  
41. Deeplearning in UE5 ? \- AI \- Epic Developer Community Forums \- Unreal Engine, accessed April 25, 2026, [https://forums.unrealengine.com/t/deeplearning-in-ue5/814046](https://forums.unrealengine.com/t/deeplearning-in-ue5/814046)  
42. InterProcessPyObjects \- PyPI, accessed April 25, 2026, [https://pypi.org/project/InterProcessPyObjects/](https://pypi.org/project/InterProcessPyObjects/)  
43. DIFFUSION MODELS ARE REAL-TIME GAME ENGINES \- OpenReview, accessed April 25, 2026, [https://openreview.net/pdf?id=P8pqeEkn1H](https://openreview.net/pdf?id=P8pqeEkn1H)  
44. Diffusion Models Are Real-Time Game Engines \- arXiv, accessed April 25, 2026, [https://arxiv.org/html/2408.14837v1](https://arxiv.org/html/2408.14837v1)  
45. Learning Agents PyTorch Flexibility and Non-Policy .Onnx Support, accessed April 25, 2026, [https://forums.unrealengine.com/t/learning-agents-pytorch-flexibility-and-non-policy-onnx-support/1726063](https://forums.unrealengine.com/t/learning-agents-pytorch-flexibility-and-non-policy-onnx-support/1726063)  
46. Bridging the Gap: Using PyTorch for Intelligent Agent Design in Game Environments, accessed April 25, 2026, [https://discuss.pytorch.org/t/bridging-the-gap-using-pytorch-for-intelligent-agent-design-in-game-environments/224642](https://discuss.pytorch.org/t/bridging-the-gap-using-pytorch-for-intelligent-agent-design-in-game-environments/224642)  
47. Utilizing Tokenizers and LibTorch Plugins in Unreal Engine 5 : r/pytorch \- Reddit, accessed April 25, 2026, [https://www.reddit.com/r/pytorch/comments/1947r2y/utilizing\_tokenizers\_and\_libtorch\_plugins\_in/](https://www.reddit.com/r/pytorch/comments/1947r2y/utilizing_tokenizers_and_libtorch_plugins_in/)  
48. Converting Models \- llama.cpp \- Mintlify, accessed April 25, 2026, [https://mintlify.com/ggml-org/llama.cpp/models/converting-models](https://mintlify.com/ggml-org/llama.cpp/models/converting-models)  
49. How to implement a shared buffer? \- c++ \- Stack Overflow, accessed April 25, 2026, [https://stackoverflow.com/questions/6956170/how-to-implement-a-shared-buffer](https://stackoverflow.com/questions/6956170/how-to-implement-a-shared-buffer)  
50. Using Windows Shared Memory in Unreal Engine because the Unreal Engine API for shared memory does not work on Windows. \- GitHub Gist, accessed April 25, 2026, [https://gist.github.com/jgcoded/5469a4d06c60519693bc](https://gist.github.com/jgcoded/5469a4d06c60519693bc)  
51. Programming Real-Time Sound in Python \- MDPI, accessed April 25, 2026, [https://www.mdpi.com/2076-3417/10/12/4214](https://www.mdpi.com/2076-3417/10/12/4214)  
52. Minimizing Audio Latency on Windows 10 with WASAPI \- Donya Quick's, accessed April 25, 2026, [https://www.donyaquick.com/minimizing-audio-latency-on-windows-10-with-wasapi/](https://www.donyaquick.com/minimizing-audio-latency-on-windows-10-with-wasapi/)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAVCAYAAAAq05ytAAADMUlEQVR4XpVWO2gVQRS9gwrGBEI0GIOK8RNBBAVT+evUQlHEDwjROo2inRpEgwp+IKABEUSUNBpBEFFiocjTFBYW9hILKytLC0HUc+be2Z15s/tecuDs3D33zszdu3f2PRHC+Wtr+Jg2geZuE5Uhi1chlbOglqiPrvOUz9cyovKmFnFUnT0/pCWuScnVPIjpFaiOj1G1YyTUuQ294CfwH+l0/AEOgavAL8GndF8xbtSp7qTFB77ELp3qmw/qUlPHedHFT5dSMWHUfEf0NnnULRjewx5QsXS3tFsiBGoSw/7pnU+web1RXJjYcCSbSy6Be1NpfkhrkOMgvNycSUgUOQB+i5P2UPdm8DbsRYWeId2xXLrp0avhG3wPjL/gZKRzxnU474j2nyXmF1oI3hBNLkW2Z8XGFVKCaB6b/ZckiXntpmhvsZrq00m7cbkY7kq9fs9Mj5POnFL4Q2LvQJ4svp674AZwyKVJd4H3wdX+rmrRZmQxFZ+hTFClH/wONkQ3ZkOfswCftGPS+jngIRgxX8V6ijrdo955FfwT+/sdE3PyWbRKj8Dl5tsE/gQbiFmP8R7YFa9d2mbVbyypM7N7wA+R6AUmxapdAY9HPq2mkxlMvizJ5yFgLgkZ4tA8fiukmVjg62uInswpTOjgLJvsE3P6yXgq2n/pyjp0YDiB8TmEcdjdsNfCfoLxGLgTfAbylK8UPTxvMPcoV7CV2CYf47XZO+yh3xh54go4Ju180jwA7LcqdCPmBUZuQhwG92PuGYz7wFnY29XlJkUTYuKDohXqs3kT0B8wKDwzbU54CIHfKJP8hf3UgHGNN2V8DDcCfRbGKdHv3Ti4DBx0PChOHjPIHnIa9i6byJH3fGOhv4KvSA7VcL1RooUFbAOXxoIlHWw+1C0XTSo84pMKP2frRCvEV0mMGQkeMv6h6Eu3LhCr8d+hpLqFZZgQX6lCXwGuEVbByVsJLeDkEK6vwMXepyd9h+grZw+yHVi9dIN44zS9tmASU6KV4au8AOIA+VM2Lb6f/Cpj5ifYY69FW+SA6KFi1c+a3zCH3dtggfD/XfqjTm1JWXXvoxbA+86oEBx6/gOMFHHk77kBGwAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAYCAYAAACBbx+6AAADnElEQVR4Xq1WTYiOURQ+NzM1MvKbn1gMofxs5Gc1KUIUO8o0bCw0mrKZhWRhSpIFRaRkKxsWiuw0ZeFvYTMoTChZ0JiVhWR4nnvu+92/977zTc1Tz3fvPefce88993znviIpTCpoD3ZazdxQlKmdIJNPG427lDEN0xT7wDEs8BTtM9dnO4I136K9FFnPHMouN8SgA7wArrUjI734+YjeamfYi+ZkOimD0y9Cby/aQ+B6cFaoDGFFmVc1hjlWgSeC8WnwEdjlxjiA7PHqHNxlB5qXaB+D/SSET6DhybdF1h47wR/gP9Jo+xM8Fticr/SOD8Bl4HynZ7TviUa8whJwYTAOYKRTNF8+Se5YJ5y4hXYC3JzoQtwGJ8HddhQHGdduXqA9KjaC2Q2sgOi9VHMd/GVF9oYO3RQbFbM91ATYJOrwddiYfA1ZAL6C6LNw80qpzS7wIfo9KqwQLcDr1/ytQ+yvDOB3ErKBeJ+gZ2Q5fr+Ab8DFqVo0z8chCHOQeX8KvAjOjs+XIc3fJB4ea8Bv4ChMmDMOJpqAfuUwyb5KPZjrzE1uTMyB+oZoHseLhVB5l1Fnw/wtYlh0o+E8ug4qWAl+FedwZiNyDYZ/RK92HfgafA7Oi6xidGOdc2jvgL9F6/BVsMdq801MN35GoKg2quS+60E97Vjg5yY2Nn/FHsYMor0r6izTjA+DR7Z0JmhEcs3hZNf3Il61vQkvatkgf804Rn8xOiv6Jz4COe3pPEtWm4gPYEeByDlsXNQUNWfmtTJirLUbKUhs+p1zZ4xXLQXfiVYWVpgysthk67fAfzv/9WOiG7SQRJG1k/V1qLAQ669Lq8hiWKr/R+JVo3NFgbFXxSurosDHgy8S6+FlN0ZdNhNGHw6OFX7RKn+jQzt1VbsZaR+QzKEyksBZ8OXionSoDzzs5ChHZtDoQ3AFnO3kHnYNswU/v8Q+qybN1Q7Y8LlllHlLCWLPdblIlMPp+RR/EL1W1ELDbwi+9Yw0Xyma8RHQCOskPqGs3+H3wXco+9yaqOn2myTUj2Iu636Euii2RvkBWhI6s1X06+yg6FdUWMgPwJT64gYZplC3g+JeNWsfh5RXPQQlHgW5b+rSom5mCY2mjcoG+Hn7xV8lc7z0UZSg/Ap7hBauHzcJpoquCuaAZ1x0N6TKOtS4kQjaOUxpbu2gVhCjUd2odAidbse+Ae0sVNbMNNxO7mYiNDqRKTNBLdo5vEWmLqfNf4R8ke4RR7dnAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAVCAYAAAAnzezqAAACqElEQVR4XpVWPWtVQRCdAS0eChYBg2CKiIVouiAiWqrYPBErQTtBLYKtjUWCiIKgAT+QKAQLC0UrBS3FnyCChQpGYgQtrGKhYDyzM/t1d25iDpw3u2dm587s3b08ogTOw95xn8dXa3AVX0X1Le9LtV74eXy1QRMWBFN9Z8+sgzLP6pH/A6cgJ2cjmTAKvgdX1slX4ADcjUQfkW2FRefge4vxdthJ6F86696AI6S4bJanzCnB98E5JJoLtiCrPo/4r5gftcURD8G/4JGOLn0+An+Beyu1wBiUD7BLcOxMqr+lkxg/Ju0+OeG+ot3z0KTsDAXwH9iDSVVsDL8We5F0F6ajN6CuVGY3wRN5mkxcb76o8z78LJtv2OnpcB4SjcMswi6yjqNeYgJ8Bm7Okt1ppnOkD5FCIgbQ78HOsxWQ4jXHnSI2PG6abBeaRwc334I92XVYoUPSA6gFaILj4AXTiuJCEadIaY/SNsbxI7sg52Es6wHS/Qtwi1OcQN69POSBLRqBuYuxnPjoi7sjN0R2Ju5kSikDuRoWnLZLzA3udl/WHq4cLbPeBlHPsO6AQAtgKS6EX6Lw/v1W5BYskX4bRq2IPRg/p3x/qSgujMkKAJ+Cu0jffbwph0ivqBQnua6CG8zX1CGZZ0k/LFP2nBnwdA5wsQP8Bic+NDyLGDn9VBfHT2CvQZIiDH42CfhBugsHwJfg1jKg072YbfhZwOw3ZterEOK4O7ILM1wsqlCuAG+TnoXv4PnsimhyyCf9E+nrs49Zek0ojhaoONx+3zUmEPQT9h2t1b1CTvRrssMbkN1SwGcI+hqrZU2sjbX4s+CxwlXDAg1yqPZjtslpT3xyJgZ+741WV9W4DY3udFGiie+FszhjjaSNUGJVZwdNN47Ul68JLKX6/+A/5RN4R408v+QAAAAASUVORK5CYII=>
