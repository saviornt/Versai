// =============================================================================
// Versai - SharedMemory Plugin
// UNiagaraDataInterfaceVersai - UE 5.7 Verified Implementation
// =============================================================================

#include "UNiagaraDataInterfaceVersai.h"
#include "HAL/PlatformMemory.h"
#include "GenericPlatform/GenericPlatformMemory.h"
#include "NiagaraTypes.h"
#include "NiagaraDataInterface.h"
#include "VectorVM.h"

#include "VizStructs.h"


UNiagaraDataInterfaceVersai::UNiagaraDataInterfaceVersai()
{
	SharedMemoryName = TEXT("versai_telemetry_shm");
}

#if WITH_EDITORONLY_DATA
void UNiagaraDataInterfaceVersai::GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
	Super::GetFunctionsInternal(OutFunctions);

	// GetLatestFrameId
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetLatestFrameId");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetIntDef(), TEXT("FrameId"));
	}

	// GetLoss
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetLoss");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetFloatDef(), TEXT("Loss"));
	}

	// GetNeuronCount
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetNeuronCount");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetIntDef(), TEXT("Count"));
	}
	
	// GetNeuronData
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetNeuronData");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Inputs.Emplace(FNiagaraTypeDefinition::GetIntDef(), TEXT("NeuronIndex"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetVec3Def(), TEXT("OutPosition"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetFloatDef(), TEXT("OutActivation"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetFloatDef(), TEXT("OutDensity"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetFloatDef(), TEXT("OutGradientMag"));
	}
}
#endif

void UNiagaraDataInterfaceVersai::GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc)
{
	if (BindingInfo.Name == TEXT("GetLatestFrameId"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&GetLatestFrameId);
	}
	else if (BindingInfo.Name == TEXT("GetLoss"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&GetLoss);
	}
	else if (BindingInfo.Name == TEXT("GetNeuronCount"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&GetNeuronCount);
	}
	else if (BindingInfo.Name == TEXT("GetNeuronData"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&GetNeuronData);
	}
}

// -----------------------------------------------------------------------------
// Per-Instance Data (shared memory)
// -----------------------------------------------------------------------------
bool UNiagaraDataInterfaceVersai::CopyToInternal(UNiagaraDataInterface* Destination) const
{
	if (!Super::CopyToInternal(Destination)) return false;
	auto* Other = CastChecked<UNiagaraDataInterfaceVersai>(Destination);
	Other->SharedMemoryName = SharedMemoryName;
	return true;
}

void* UNiagaraDataInterfaceVersai::CreatePerInstanceData(void* PerInstanceDataInit, FNiagaraSystemInstance* SystemInstance)
{
	FNDIVersaiInstanceData* InstData = new FNDIVersaiInstanceData();
	
	// Map (open) the shared memory region
	InstData->SharedMemoryRegion = FPlatformMemory::MapNamedSharedMemoryRegion(
		*SharedMemoryName, 
		false, 
		FPlatformMemory::ESharedMemoryAccess::Read,
		0
	);
 
	return InstData;
}

void UNiagaraDataInterfaceVersai::DestroyPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance)
{
	if (FNDIVersaiInstanceData* InstData = static_cast<FNDIVersaiInstanceData*>(PerInstanceData))
	{
		if (InstData->SharedMemoryRegion)
		{
			FPlatformMemory::UnmapNamedSharedMemoryRegion(InstData->SharedMemoryRegion);
			InstData->SharedMemoryRegion = nullptr;
		}
		delete InstData;
	}
}

bool UNiagaraDataInterfaceVersai::Equals(const UNiagaraDataInterface* Other) const
{
	if (!Super::Equals(Other))
	{
		return false;
	}

	const UNiagaraDataInterfaceVersai* OtherVersai = Cast<UNiagaraDataInterfaceVersai>(Other);
	if (!OtherVersai)
	{
		return false;
	}

	// Compare the properties that make this DI unique
	return SharedMemoryName == OtherVersai->SharedMemoryName;
}

// -----------------------------------------------------------------------------
// VM Implementations using VectorVM (UE 5.7 Fix)
// -----------------------------------------------------------------------------

void UNiagaraDataInterfaceVersai::GetLatestFrameId(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FUserPtrHandler<FNDIVersaiInstanceData> InstData(Context);
	FNDIOutputParam<int32> OutFrameId(Context);
 
    int32 FrameId = 0;
    if (InstData.Get() && InstData->SharedMemoryRegion && InstData->SharedMemoryRegion->GetAddress())
    {
        const FLayerFrameHeader* Header = static_cast<const FLayerFrameHeader*>(InstData->SharedMemoryRegion->GetAddress());
        FrameId = static_cast<int32>(Header->FrameId);
    }
    for (int32 i = 0; i < Context.GetNumInstances(); ++i)
        OutFrameId.SetAndAdvance(FrameId);
}
 
void UNiagaraDataInterfaceVersai::GetLoss(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FUserPtrHandler<FNDIVersaiInstanceData> InstData(Context);
	FNDIOutputParam<float> OutLoss(Context);
 
    float Loss = 0.0f;
    if (InstData.Get() && InstData->SharedMemoryRegion && InstData->SharedMemoryRegion->GetAddress())
    {
        const FLayerFrameHeader* Header = static_cast<const FLayerFrameHeader*>(InstData->SharedMemoryRegion->GetAddress());
        Loss = Header->Loss;
    }
    for (int32 i = 0; i < Context.GetNumInstances(); ++i)
        OutLoss.SetAndAdvance(Loss);
}

void UNiagaraDataInterfaceVersai::GetNeuronCount(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FUserPtrHandler<FNDIVersaiInstanceData> InstData(Context);
	FNDIOutputParam<int32> OutCount(Context);

	int32 Count = 0;
	if (InstData.Get() && InstData->SharedMemoryRegion && InstData->SharedMemoryRegion->GetAddress())
	{
		const FLayerFrameHeader* Header = static_cast<const FLayerFrameHeader*>(InstData->SharedMemoryRegion->GetAddress());
		Count = Header->NeuronCount;
	}
	for (int32 i = 0; i < Context.GetNumInstances(); ++i)
		OutCount.SetAndAdvance(Count);
}
 
void UNiagaraDataInterfaceVersai::GetNeuronData(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FUserPtrHandler<FNDIVersaiInstanceData> InstData(Context);
	VectorVM::FExternalFuncInputHandler<int32> NeuronIndexParam(Context);
 
    FNDIOutputParam<FVector3f> OutPos(Context);
    FNDIOutputParam<float> OutActivation(Context);
    FNDIOutputParam<float> OutDensity(Context);
    FNDIOutputParam<float> OutGradientMag(Context);
 
    for (int32 i = 0; i < Context.GetNumInstances(); ++i)
    {
        int32 Index = NeuronIndexParam.GetAndAdvance();
        if (InstData.Get() && InstData->SharedMemoryRegion && InstData->SharedMemoryRegion->GetAddress())
        {
            const FLayerFrameHeader* Header = static_cast<const FLayerFrameHeader*>(InstData->SharedMemoryRegion->GetAddress());
            const FNeuronPCGPoint* Neurons = reinterpret_cast<const FNeuronPCGPoint*>(
                static_cast<const uint8*>(InstData->SharedMemoryRegion->GetAddress()) + sizeof(FLayerFrameHeader));
 
            if (Index >= 0 && Index < Header->NeuronCount)
            {
                const FNeuronPCGPoint& Neuron = Neurons[Index];
                OutPos.SetAndAdvance(FVector3f(Neuron.Position));
                OutActivation.SetAndAdvance(Neuron.Activation);
                OutDensity.SetAndAdvance(Neuron.Density);
                OutGradientMag.SetAndAdvance(Neuron.GradientMag);
                continue;
            }
        }
    	
    	// Fallback
        OutPos.SetAndAdvance(FVector3f::ZeroVector);
        OutActivation.SetAndAdvance(0.0f);
        OutDensity.SetAndAdvance(0.0f);
        OutGradientMag.SetAndAdvance(0.0f);
    }
}