import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
VAL=0.8   # lensed-view brightness
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='BlackHole_RMDisk':
        smc=a.get_component_by_class(unreal.StaticMeshComponent)
        mid=smc.get_material(0)
        if isinstance(mid,unreal.MaterialInstanceDynamic):
            mid.set_scalar_parameter_value('Brightness',VAL)
            print('disk Brightness ->',VAL)
        else:
            print('material is not a MID:',type(mid))
les.save_current_level()
