// =============================================================================
// Versai - SharedMemory Plugin
// Main module implementation
// =============================================================================

#include "SharedMemory.h"
#include "Modules/ModuleManager.h"

void FSharedMemoryModule::StartupModule()
{
	// Module is ready - no heavy init needed for now
}

void FSharedMemoryModule::ShutdownModule()
{
	// Clean shutdown
}

IMPLEMENT_MODULE(FSharedMemoryModule, SharedMemory)