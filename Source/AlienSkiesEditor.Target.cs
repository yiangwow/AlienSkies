using UnrealBuildTool;
using System.Collections.Generic;

public class AlienSkiesEditorTarget : TargetRules
{
	public AlienSkiesEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		bOverrideBuildEnvironment = true;  // allow building against the installed (binary) engine
		ExtraModuleNames.Add("AlienSkies");
	}
}
