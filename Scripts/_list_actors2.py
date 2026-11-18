"""List all level actors via world subsystem (bypasses the EditorActorSubsystem bug)."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
print(f'Total actors: {len(actors)}')
for a in sorted(actors, key=lambda x: x.get_actor_label()):
    cls = a.get_class().get_name()
    loc = a.get_actor_location()
    print(f'  {a.get_actor_label():45s} {cls:35s} ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')
