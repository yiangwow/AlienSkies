import unreal, sys
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
show = '--show' in sys.argv
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='BlackHole_RMDisk':
        a.set_is_temporarily_hidden_in_editor(not show)
print('disk', 'shown' if show else 'hidden')
