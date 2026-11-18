"""List all Brush (BSP) actors and find/restore SM_SkySphere."""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

actors = eas.get_all_level_actors()

# List brushes
brushes = [a for a in actors if 'Brush' in a.get_class().get_name() or 'Geometry' in a.get_class().get_name()]
print(f'Brushes/Geometry actors ({len(brushes)}):')
for b in brushes:
    loc = b.get_actor_location()
    print(f'  {b.get_actor_label():40s} ({b.get_class().get_name()}) @ ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')

# List all static mesh actors
smas = [a for a in actors if a.get_class().get_name() == 'StaticMeshActor']
print(f'\nStaticMeshActors ({len(smas)}):')
for s in smas:
    loc = s.get_actor_location()
    print(f'  {s.get_actor_label():40s} @ ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')

print(f'\nTotal actors: {len(actors)}')
