using UnrealBuildTool;

public class AlienSkies : ModuleRules
{
    public AlienSkies(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput",
            "RenderCore",
            "Renderer"
        });
    }
}
