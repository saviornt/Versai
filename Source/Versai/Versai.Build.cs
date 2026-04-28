// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class Versai : ModuleRules
{
	public Versai(ReadOnlyTargetRules Target) : base(Target)
	{
		// Use the latest UE5 include order convention
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
	
		PublicDependencyModuleNames.AddRange(new string[] {
			"Core","CoreUObject", "Engine", "InputCore", "UMG",
			"EnhancedInput", "CommonUI", "Niagara", "VectorVM", 
			"AudioExtensions", "MetasoundFrontend", "MetasoundStandardNodes",
			"AudioModulation", "MetasoundEngine"
			});

		PrivateDependencyModuleNames.AddRange(new string[] {  });

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });
		
		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
