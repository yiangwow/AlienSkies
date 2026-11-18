"""Re-assign M_SpiralGalaxy to all Galaxy_ actors whose MID got orphaned."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
les   = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

mat = unreal.load_asset('/Game/AlienSkies/Materials/M_SpiralGalaxy')
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)

fixed = 0
for a in actors:
    if not a.get_actor_label().startswith('Galaxy_'):
        continue
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    if not smc:
        continue
    cur = smc.get_material(0)
    # Re-create the MID from the current asset regardless — heals orphans
    smc.create_dynamic_material_instance(0, mat)
    fixed += 1

les.save_current_level()
print(f'Re-assigned M_SpiralGalaxy on {fixed} galaxy actors.')
