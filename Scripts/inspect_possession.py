import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

# BP_Camera level actor: auto-possess + class
cam = None
ps = None
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl == 'BP_Camera':
        cam = a
    if a.get_class().get_name() == 'PlayerStart':
        ps = a

if cam:
    try:
        app = cam.get_editor_property('auto_possess_player')
        print(f'BP_Camera auto_possess_player = {app}')
    except Exception as e:
        print(f'auto_possess read err: {e}')
    try:
        aiapp = cam.get_editor_property('auto_possess_ai')
        print(f'BP_Camera auto_possess_ai = {aiapp}')
    except Exception as e:
        pass
    print(f'BP_Camera class = {cam.get_class().get_name()}')
    print(f'BP_Camera location = {cam.get_actor_location()}')
else:
    print('BP_Camera NOT in level')

print(f'PlayerStart present = {ps is not None}')

# World settings GameMode override
world = ues.get_editor_world()
ws = world.get_world_settings()
gm = ws.get_editor_property('default_game_mode')
print(f'World GameMode override = {gm}')

# Project default game mode
try:
    import configparser
except Exception:
    pass
