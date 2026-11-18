"""Apply core=90000 (fills inside the bright ring, blocks background leak), photon ring just
outside, CaptureR=34000. Save."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
core=disk=ring=None
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl=='BlackHole_Core': core=a
    elif lbl=='BlackHole_RMDisk': disk=a
    elif lbl=='BlackHole_PhotonRing': ring=a
R=90000.0
core.set_actor_scale3d(unreal.Vector(R/160.0, R/160.0, R/160.0))
ring.set_actor_scale3d(unreal.Vector(R*1.04/160.0, R*1.04/160.0, R*1.04/160.0))
disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0).set_scalar_parameter_value('CaptureR', 34000.0)
les.save_current_level()
print(f'core={R}, ring={R*1.04}, CaptureR=34000. Saved.')
