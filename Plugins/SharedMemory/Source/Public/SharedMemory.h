// =============================================================================
// Versai - SharedMemory Plugin
// Main module declaration
// =============================================================================

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FSharedMemoryModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};