import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

GM = '/Game/AlienSkies/Blueprints/BP_SpaceGameMode'
print(f'BP_SpaceGameMode exists: {unreal.EditorAssetLibrary.does_asset_exist(GM)}')
if unreal.EditorAssetLibrary.does_asset_exist(GM):
    gm = unreal.load_asset(GM)
    cdo = unreal.get_default_object(gm.generated_class())
    dpc = cdo.get_editor_property('default_pawn_class')
    print(f'  DefaultPawnClass = {dpc.get_name() if dpc else None}')

ws = ues.get_editor_world().get_world_settings()
gmo = ws.get_editor_property('default_game_mode')
print(f'World GameMode override = {gmo.get_name() if gmo else None}')

cams = [a for a in eas.get_all_level_actors() if a.get_class().get_name()=='BP_Camera_C']
ps   = [a for a in eas.get_all_level_actors() if a.get_class().get_name()=='PlayerStart']
print(f'BP_Camera actors in level: {len(cams)}')
print(f'PlayerStart actors in level: {len(ps)}')
for p in ps:
    print(f'  PlayerStart at {p.get_actor_location()} rot {p.get_actor_rotation()}')
