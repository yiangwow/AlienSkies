"""List all actors with mesh/material detail to find stone wall geometry."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# Force loading any world partition cells near origin (where test scene walls would be)
world = unreal.EditorLevelLibrary.get_editor_world()
actors = eas.get_all_level_actors()
print(f'Total: {len(actors)}')
KNOWN_PREFIXES = (
    'BlackHole_', 'Galaxy_', 'HeroStar_', 'VolGalaxy_',
    'BP_Camera', 'BP_SceneDirector', 'PPV_DeepSpace', 'SM_SkySphere',
    'DirectionalLight', 'SkyLight', 'PlayerStart', 'WorldDataLayers',
    'WorldPartitionMiniMap', 'WorldSettings',
)
unknowns = []
for a in sorted(actors, key=lambda x: x.get_actor_label()):
    label = a.get_actor_label()
    cls = a.get_class().get_name()
    loc = a.get_actor_location()
    known = any(label.startswith(p) for p in KNOWN_PREFIXES)
    if not known:
        unknowns.append(a)
        # Try to get mesh info for StaticMeshActors
        mesh_name = ''
        if cls == 'StaticMeshActor':
            smc = a.get_component_by_class(unreal.StaticMeshComponent)
            if smc:
                m = smc.get_editor_property('static_mesh')
                mesh_name = m.get_name() if m else '<no mesh>'
        print(f'  UNKNOWN: {label:40s} {cls:35s} ({loc.x:.0f},{loc.y:.0f},{loc.z:.0f}) mesh={mesh_name}')

if not unknowns:
    print('  (no unknown actors found)')
print(f'Unknown actors: {len(unknowns)}')
