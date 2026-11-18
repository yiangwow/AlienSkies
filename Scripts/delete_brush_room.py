"""Delete the original test scene BSP Brush room (the stone wall box).
Only destroys actors with class name 'Brush' — never touches WorldDataLayers,
WorldSettings, WorldPartitionMiniMap, or any StaticMeshActor.
"""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas   = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les   = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)

SAFE_SKIP = {'WorldDataLayers', 'WorldSettings', 'WorldPartitionMiniMap',
             'StaticMeshActor', 'PostProcessVolume', 'DirectionalLight', 'SkyLight'}

deleted = []
for a in actors:
    cls = a.get_class().get_name()
    lbl = a.get_actor_label()
    if cls == 'Brush' and lbl not in ('WorldSettings', 'WorldSettings-1'):
        print(f'  Deleting Brush: {lbl} ({cls})')
        eas.destroy_actor(a)
        deleted.append(lbl)

if deleted:
    les.save_current_level()
    print(f'Deleted {len(deleted)} Brush actor(s): {deleted}')
else:
    print('No Brush actors found to delete.')
