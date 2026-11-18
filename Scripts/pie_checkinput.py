import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
gw = ues.get_game_world()
if not gw:
    print('PIE not running'); 
else:
    pcs = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.PlayerController)
    for pc in pcs:
        w = unreal.Key(); w.set_editor_property('key_name','W')
        try:
            down_w = pc.is_input_key_down(w)
            print(f'W down: {down_w}')
        except Exception as e:
            print(f'is_input_key_down err: {e}')
        try:
            mx, my = pc.get_input_mouse_delta()
            print(f'mouse delta: {mx},{my}')
        except Exception as e:
            print(f'mouse delta err: {e}')
