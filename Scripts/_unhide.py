import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l.startswith('Galaxy_') or l.startswith('VolGalaxy'):
        a.set_is_temporarily_hidden_in_editor(False)
les.save_current_level(); print('galaxies unhidden + saved')
