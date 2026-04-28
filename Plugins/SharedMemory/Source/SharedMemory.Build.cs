// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class SharedMemory : ModuleRules
{
	public SharedMemory(ReadOnlyTargetRules Target) : base(Target)
	{
		// Use the latest UE5 include order convention
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"Niagara",
			"NiagaraCore",
			"VectorVM"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		// Public include paths for other modules
		PublicIncludePaths.AddRange(new string[]
		{
		});
	}
}