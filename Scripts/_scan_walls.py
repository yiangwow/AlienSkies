"""Find any actors near the origin that could be stone wall geometry."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)

print('=== All StaticMeshActors + their mesh assets ===')
for a in actors:
    cls = a.get_class().get_name()
    loc = a.get_actor_location()
    lbl = a.get_actor_label()
    dist = (loc.x**2 + loc.y**2 + loc.z**2) ** 0.5

    if 'StaticMesh' in cls or 'Brush' in cls or 'Geometry' in cls:
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        mesh_name = ''
        if smc:
            m = smc.get_editor_property('static_mesh')
            if m:
                mesh_name = m.get_path_name()
        print(f'  {lbl:45s} dist={dist:>10.0f}  mesh={mesh_name}')

print()
print('=== Non-standard actors (not Galaxy/Star/BlackHole/etc) ===')
KNOWN = {'Galaxy','Star','HeroStar','BlackHole','SM_SkySphere','PPV','BP_','Vol',
         'Player','World','AbstractNav','Default','Gameplay','DirectionalLight',
         'SkyLight','Brush','Actor '}
for a in actors:
    lbl = a.get_actor_label()
    cls = a.get_class().get_name()
    if not any(k in lbl for k in KNOWN):
        loc = a.get_actor_location()
        print(f'  {lbl:45s} {cls:35s} ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')
