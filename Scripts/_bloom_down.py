import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='PPV_DeepSpace':
        s=a.get_editor_property('settings')
        s.set_editor_property('bloom_intensity',0.22)
        a.set_editor_property('settings',s)
        print('bloom -> 0.22')
les.save_current_level()
