import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
print(f'Total actors: {len(actors)}')
for a in sorted(actors, key=lambda x: x.get_actor_label()):
    cls = a.get_class().get_name()
    loc = a.get_actor_location()
    print(f'  {a.get_actor_label():40s} {cls:35s} ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')
