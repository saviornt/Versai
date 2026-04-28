#pragma once

#include "CoreMinimal.h"
#include "NiagaraDataInterface.h"
#include "HAL/PlatformMemory.h"
#include "VectorVM.h"

#include "UNiagaraDataInterfaceVersai.generated.h"

// Forward declares for your shared struct
struct FLayerFrameHeader;
struct FNeuronPCGPoint;

// Instance data struct for each system using this DI
struct FNDIVersaiInstanceData
{
    // Cross-platform shared memory abstraction
    FPlatformMemory::FSharedMemoryRegion* SharedMemoryRegion = nullptr;

    FNDIVersaiInstanceData() = default;
    ~FNDIVersaiInstanceData() = default;
};

UCLASS(EditInlineNew, Category = "Versai", meta = (DisplayName = "Shared Memory Data Interface"))
class SHAREDMEMORY_API UNiagaraDataInterfaceVersai : public UNiagaraDataInterface
{
    GENERATED_BODY()

public:
    UNiagaraDataInterfaceVersai();

    // The shared memory name to open. Can be edited in Niagara/Blueprints.
    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    FString SharedMemoryName;

    // --- Required NI DI overrides ---
#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif
    
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc) override;
    virtual bool CopyToInternal(UNiagaraDataInterface* Destination) const override;
    
    virtual void* CreatePerInstanceData(void* PerInstanceDataInit, FNiagaraSystemInstance* SystemInstance);
    virtual void DestroyPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance) override;
    
    virtual bool Equals(const UNiagaraDataInterface* Other) const override;
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override { return Target == ENiagaraSimTarget::CPUSim; }

    // --- Static Niagara VM function signatures ---
    static void GetLatestFrameId(FVectorVMExternalFunctionContext& Context);
    static void GetLoss(FVectorVMExternalFunctionContext& Context);
    static void GetNeuronCount(FVectorVMExternalFunctionContext& Context);
    static void GetNeuronData(FVectorVMExternalFunctionContext& Context);
};