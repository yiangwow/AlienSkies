import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
gw = ues.get_game_world()
if not gw:
    print('PIE not running')
else:
    print(f'game paused: {unreal.GameplayStatics.is_game_paused(gw)}')
    pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Pawn)
    for p in pawns:
        print(f'pawn tick enabled: {p.is_actor_tick_enabled()}')
        print(f'pawn CurrentYaw: {p.get_editor_property("current_yaw")}')
        print(f'pawn Velocity: {p.get_editor_property("velocity")}')
        pc = p.get_controller()
        # Is input enabled? check the PC
        print(f'controller: {pc.get_name() if pc else None}')
