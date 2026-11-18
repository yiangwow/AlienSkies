import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_RMDisk': disk = a
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_scalar_parameter_value('LensStrength', 40000.0)
les.save_current_level()
print('LensStrength=40000 (close top gap), saved.')
