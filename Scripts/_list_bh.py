import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if 'BlackHole' in l or 'BH' in l:
        print(l)
