import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if l in ('Galaxy_Hero','Galaxy_HomeDisc','HeroStar_00'):
        print(f'{l}: is_spatially_loaded = {a.get_editor_property("is_spatially_loaded")}')
