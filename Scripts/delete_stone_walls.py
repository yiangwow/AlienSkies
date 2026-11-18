"""Find and delete L_TestScene stone wall geometry (not our black hole / cosmic actors)."""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

actors = eas.get_all_level_actors()
print(f'Total actors: {len(actors)}')

# Labels we MUST keep
KEEP = {
    'BlackHole_Core', 'BlackHole_PhotonRing', 'BlackHole_RMDisk',
    'BlackHole_JetN', 'BlackHole_JetS', 'BlackHole_JetSheathN', 'BlackHole_JetSheathS',
    'PPV_DeepSpace', 'BP_Camera', 'BP_SceneDirector', 'BP_SpaceGameMode',
}

# Class names we must keep (lights, cameras, game mode, player start, etc.)
KEEP_CLASSES = {
    'DirectionalLight', 'SkyLight', 'ExponentialHeightFog',
    'PostProcessVolume', 'PlayerStart', 'GameModeBase',
    'BP_Camera_C', 'BP_SceneDirector_C', 'BP_SpaceGameMode_C',
    'WorldSettings', 'Brush',
}

to_delete = []
for a in actors:
    label = a.get_actor_label()
    cls = a.get_class().get_name()

    # Keep our named actors
    if label in KEEP:
        continue
    # Keep by class
    if any(k in cls for k in KEEP_CLASSES):
        continue
    # Keep anything that looks like our cosmic content
    if any(x in label for x in ['Galaxy', 'Star', 'HeroStar', 'Dome', 'VolGalaxy', 'BP_']):
        continue

    print(f'  DELETING: {label:45s} ({cls})')
    to_delete.append(a)

if to_delete:
    for a in to_delete:
        eas.destroy_actor(a)
    les.save_current_level()
    print(f'\nDeleted {len(to_delete)} actors. Level saved.')
else:
    print('Nothing to delete — all actors are keepers.')
