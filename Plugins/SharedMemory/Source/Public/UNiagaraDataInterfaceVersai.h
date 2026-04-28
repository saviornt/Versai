// =============================================================================
// Versai - SharedMemory Plugin
// UNiagaraDataInterfaceVersai - zero-copy reader for Python structured buffer
// =============================================================================

#pragma once

#include "CoreMinimal.h"
#include "NiagaraDataInterface.h"
#include "VectorVM.h"               
#include "VizStructs.h"             // <-- Will be used in full reader (ignore unused warning for now)

#include "UNiagaraDataInterfaceVersai.generated.h"

UCLASS(EditInlineNew, Category = "Versai")
class SHAREDMEMORY_API UNiagaraDataInterfaceVersai : public UNiagaraDataInterface
{
	GENERATED_BODY()

public:
	UNiagaraDataInterfaceVersai();

	// ~UNiagaraDataInterface interface
#if WITH_EDITORONLY_DATA
	virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif
	virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc) override;
	virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override { return true; }

	// Shared memory name (must match VERSAI_TELEMETRY_SHM_NAME in settings.py)
	UPROPERTY(EditAnywhere, Category = "Versai")
	FString SharedMemoryName = TEXT("versai_telemetry_shm");

protected:
	virtual bool CopyToInternal(UNiagaraDataInterface* Destination) const override;

private:
	// Per-instance data (allocated by Niagara)
	struct FNDIVersaiInstanceData
	{
		void* SharedMemoryHandle = nullptr;
		void* MappedView = nullptr;
		uint64 LastFrameId = 0;
	};

	// VM functions exposed to Niagara (will be fully implemented next)
	static void GetLatestFrameId(FVectorVMExternalFunctionContext& Context);
	static void GetLoss(FVectorVMExternalFunctionContext& Context);
	static void GetNeuronCount(FVectorVMExternalFunctionContext& Context);
	static void GetNeuronData(FVectorVMExternalFunctionContext& Context);
};