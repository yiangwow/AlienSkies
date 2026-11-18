using UnrealBuildTool;
using System.Collections.Generic;

public class AlienSkiesTarget : TargetRules
{
	public AlienSkiesTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		bOverrideBuildEnvironment = true;  // allow building against the installed (binary) engine
		ExtraModuleNames.Add("AlienSkies");
	}
}
