import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

cam_bp = unreal.load_asset('/Game/AlienSkies/Blueprints/BP_Camera')
cam_class = cam_bp.generated_class()

# 1. Remove any existing placed BP_Camera (avoid dupes)
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == 'BP_Camera_C':
        eas.destroy_actor(a)

# 2. Place ONE BP_Camera at the viewing spot; it auto-possesses Player0 EARLY
SPAWN = unreal.Vector(0, 0, 10000)
cam = eas.spawn_actor_from_class(cam_class, SPAWN, unreal.Rotator(0, 0, 180))
cam.set_actor_label('BP_Camera')
cam.set_editor_property('is_spatially_loaded', False)   # always loaded across restarts
try:
    cam.set_editor_property('auto_possess_player', unreal.AutoReceiveInput.PLAYER0)
    print('placed BP_Camera, auto_possess=PLAYER0, always-loaded')
except Exception as e:
    print(f'auto_possess set err: {e}')

# 3. GameMode spawns NOTHING (no competitor for Player0)
gm = unreal.load_asset('/Game/AlienSkies/Blueprints/BP_SpaceGameMode')
cdo = unreal.get_default_object(gm.generated_class())
try:
    cdo.set_editor_property('default_pawn_class', None)
    print('GameMode DefaultPawnClass = None')
except Exception as e:
    print(f'DefaultPawnClass None err: {e}')
unreal.EditorAssetLibrary.save_loaded_asset(gm)

# 4. Keep world GameMode override
ws = ues.get_editor_world().get_world_settings()
ws.set_editor_property('default_game_mode', gm.generated_class())

# 5. Move PlayerStart to the spawn spot (cosmetic; placed cam is what's possessed)
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == 'PlayerStart':
        a.set_actor_location(SPAWN, False, False)

les.save_current_level()
print('saved')
