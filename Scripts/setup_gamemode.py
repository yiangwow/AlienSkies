import unreal

at = unreal.AssetToolsHelpers.get_asset_tools()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

GM_PATH = '/Game/AlienSkies/Blueprints/BP_SpaceGameMode'
cam_bp = unreal.load_asset('/Game/AlienSkies/Blueprints/BP_Camera')
cam_class = cam_bp.generated_class()

# Create the GameMode blueprint if missing
if unreal.EditorAssetLibrary.does_asset_exist(GM_PATH):
    gm = unreal.load_asset(GM_PATH)
else:
    bf = unreal.BlueprintFactory()
    bf.set_editor_property('parent_class', unreal.GameModeBase)
    gm = at.create_asset('BP_SpaceGameMode', '/Game/AlienSkies/Blueprints', None, bf)

gm_class = gm.generated_class()

# Set DefaultPawnClass = BP_Camera on the GameMode CDO
cdo = unreal.get_default_object(gm_class)
cdo.set_editor_property('default_pawn_class', cam_class)
print(f'GameMode DefaultPawnClass set to {cam_class.get_name()}')
unreal.EditorAssetLibrary.save_loaded_asset(gm)

# Apply as the world's GameMode override
world = ues.get_editor_world()
ws = world.get_world_settings()
ws.set_editor_property('default_game_mode', gm_class)
print('World GameMode override set to BP_SpaceGameMode')

# Move the placed BP_Camera to a good viewing spot near the galaxies
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BP_Camera':
        a.set_actor_location(unreal.Vector(0, 0, 10000), False, False)
        print('Moved BP_Camera to (0,0,10000)')
    if a.get_class().get_name() == 'PlayerStart':
        a.set_actor_location(unreal.Vector(0, 0, 10000), False, False)
        a.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
        print('Moved PlayerStart to (0,0,10000)')

les.save_current_level()
print('saved')
