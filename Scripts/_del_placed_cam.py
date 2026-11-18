import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
n = 0
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BP_Camera':
        eas.destroy_actor(a); n += 1
print(f'Deleted {n} placed BP_Camera (GameMode will spawn+possess one at PlayerStart)')
les.save_current_level()
print('saved')
