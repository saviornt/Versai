// =============================================================================
// Versai - SharedMemory Plugin
// =============================================================================

#pragma once

#include "CoreMinimal.h"

#pragma pack(push, 8)

/** 64-byte aligned frame header (matches Python structured buffer write) */
struct alignas(64) FLayerFrameHeader
{
	uint64 FrameId;
	uint32 BufferIndex;     // 0 = A (read), 1 = B (write)
	uint32 Ready;           // 1 = data is ready
	int32  LayerId;
	int32  NeuronCount;
	int32  ConnectionCount;
	float  Loss;
	uint64 Reserved[2];     // padding to 64 bytes
};

/** Neuron / PCG point (exact match to NEURON_DTYPE) */
struct alignas(64) FNeuronPCGPoint
{
	int32  Id;
	float  Activation;
	FVector Position;       // x, y, z
	float  Density;
	float  GradientMag;
	int32  LayerId;
};

/** Connection / Niagara ribbon (exact match to CONNECTION_DTYPE) */
struct alignas(64) FConnectionPCG
{
	int32  FromId;
	int32  ToId;
	float  Weight;
	float  Thickness;
};

#pragma pack(pop)