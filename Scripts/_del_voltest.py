import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
n=0
for a in eas.get_all_level_actors():
    if a.get_actor_label() in ('VolGalaxy_TEST',): eas.destroy_actor(a); n+=1
les.save_current_level()
print(f'deleted {n} leftover test galaxy')
