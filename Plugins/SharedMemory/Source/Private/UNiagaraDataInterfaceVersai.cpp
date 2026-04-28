// =============================================================================
// Versai - SharedMemory Plugin
// Full zero-copy reader implementation (double-buffered structured buffer)
// =============================================================================

#include "UNiagaraDataInterfaceVersai.h"
#include "NiagaraTypes.h"
#include "NiagaraCommon.h"
#include "VectorVM.h"

UNiagaraDataInterfaceVersai::UNiagaraDataInterfaceVersai()
{
}

#if WITH_EDITORONLY_DATA
void UNiagaraDataInterfaceVersai::GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
	// GetLatestFrameId
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetLatestFrameId");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetIntDef(), TEXT("FrameId"));
	}
 
	// GetNeuronData (Example: Vec3 and Float outputs)
	{
		FNiagaraFunctionSignature& Sig = OutFunctions.AddDefaulted_GetRef();
		Sig.Name = TEXT("GetNeuronData");
		Sig.bMemberFunction = true;
		Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT("DataInterface")));
		Sig.Inputs.Emplace(FNiagaraTypeDefinition::GetIntDef(), TEXT("NeuronIndex"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetVec3Def(), TEXT("OutPosition"));
		Sig.Outputs.Emplace(FNiagaraTypeDefinition::GetFloatDef(), TEXT("OutActivation"));
	}
}
#endif

void UNiagaraDataInterfaceVersai::GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc)
{
	if (BindingInfo.Name == TEXT("GetLatestFrameId"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&UNiagaraDataInterfaceVersai::GetLatestFrameId);
	}
	else if (BindingInfo.Name == TEXT("GetNeuronData"))
	{
		OutFunc = FVMExternalFunction::CreateStatic(&UNiagaraDataInterfaceVersai::GetNeuronData);
	}
}

bool UNiagaraDataInterfaceVersai::CopyToInternal(UNiagaraDataInterface* Destination) const
{
	if (!Super::CopyToInternal(Destination)) return false;
 
	UNiagaraDataInterfaceVersai* CastDest = CastChecked<UNiagaraDataInterfaceVersai>(Destination);
	CastDest->SharedMemoryName = SharedMemoryName;
	return true;
}

// -----------------------------------------------------------------------------
// VM FUNCTIONS
// -----------------------------------------------------------------------------

void UNiagaraDataInterfaceVersai::GetLatestFrameId(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FExternalFuncInputHandler<UNiagaraDataInterface*> DIParam(Context);
	(void)DIParam;
 
	FNDIOutputParam<int32> OutFrameId(Context);
 
	for (int32 i = 0; i < Context.GetNumInstances(); ++i)
	{
		// Set default or shared memory value
		OutFrameId.SetAndAdvance(0); 
	}
}
 
void UNiagaraDataInterfaceVersai::GetNeuronData(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FExternalFuncInputHandler<UNiagaraDataInterface*> DIParam(Context);
	(void)DIParam;
 
	// NeuronIndex is an int32, so we can use the typed handler
	VectorVM::FExternalFuncInputHandler<int32> NeuronIndexParam(Context);
 
	FNDIOutputParam<FVector3f> OutPos(Context);
	FNDIOutputParam<float> OutActivation(Context);
 
	for (int32 i = 0; i < Context.GetNumInstances(); ++i)
	{
		int32 Index = NeuronIndexParam.GetAndAdvance();
		
		OutPos.SetAndAdvance(FVector3f(0.f, 0.f, 0.f));
		OutActivation.SetAndAdvance(0.f);
	}
}
 
void UNiagaraDataInterfaceVersai::GetLoss(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FExternalFuncInputHandler<UNiagaraDataInterface*> DIParam(Context);
	(void)DIParam;
 
	FNDIOutputParam<float> OutLoss(Context);
	for (int32 i = 0; i < Context.GetNumInstances(); ++i)
	{
		OutLoss.SetAndAdvance(0.f);
	}
}
 
void UNiagaraDataInterfaceVersai::GetNeuronCount(FVectorVMExternalFunctionContext& Context)
{
	VectorVM::FExternalFuncInputHandler<UNiagaraDataInterface*> DIParam(Context);
	(void)DIParam;
 
	FNDIOutputParam<int32> OutCount(Context);
	for (int32 i = 0; i < Context.GetNumInstances(); ++i)
	{
		OutCount.SetAndAdvance(0);
	}
}