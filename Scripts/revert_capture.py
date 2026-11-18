"""Revert disk CaptureR 26000 -> 34000. Lowering it let additive disk gas leak in FRONT of the
opaque core (NOT occluded), filling the center gold and killing the black void in Standalone.
(SceneCapture didn't show this — it omits the additive disk pass.) Restore the clean void."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_RMDisk': disk = a
if disk is None:
    print('RMDisk not found - PIE/Standalone running?')
else:
    m = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
    m.set_scalar_parameter_value('CaptureR', 34000.0)
    les.save_current_level()
    print('Reverted CaptureR -> 34000, saved.')
