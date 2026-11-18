import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('BlackHole'):
        a.set_is_temporarily_hidden_in_editor(False)
print('all BlackHole actors shown')
