"""Revert the regression: CaptureR 32000 -> 15000 so the bright inner disk gas renders right
up to the core and the ring hugs tight (no dark gap). Save."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_RMDisk':
        disk = a
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_scalar_parameter_value('CaptureR', 15000.0)
les.save_current_level()
print('Reverted CaptureR -> 15000 (ring hugs core, no gap). Saved.')
