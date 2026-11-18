"""Open the AlienSkies level and attach M_PPLensing2 to PPV_DeepSpace."""
import unreal

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# Find AlienSkies level asset
LEVEL_PATH = '/Game/AlienSkies/Levels/AlienSkies'
if not unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
    # Try listing levels
    levels = unreal.EditorAssetLibrary.list_assets('/Game/AlienSkies/Levels/', recursive=False)
    print('Available levels:', levels)
else:
    print(f'Opening {LEVEL_PATH}')
    les.load_level(LEVEL_PATH)
    import time; time.sleep(2)

    ppvs = [a for a in eas.get_all_level_actors() if 'PostProcess' in a.get_class().get_name()]
    print('PPVs after load:', [(a.get_actor_label(), a.get_class().get_name()) for a in ppvs])
