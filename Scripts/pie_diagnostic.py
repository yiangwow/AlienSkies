import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
gw = None
try:
    gw = ues.get_game_world()
except Exception as e:
    print(f'get_game_world err: {e}')

if not gw:
    print('PIE NOT RUNNING (no game world). Press Alt+P and leave it playing, then re-run.')
else:
    print(f'PIE world: {gw.get_name()}')
    pcs = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.PlayerController)
    print(f'PlayerControllers: {len(pcs)}')
    for pc in pcs:
        pawn = pc.get_controlled_pawn() if hasattr(pc,'get_controlled_pawn') else None
        try:
            pawn = pc.get_editor_property('pawn')
        except Exception:
            pass
        print(f'  PC {pc.get_name()} -> pawn = {pawn.get_class().get_name() if pawn else "NONE (unpossessed!)"}')
        if pawn:
            print(f'     pawn loc = {pawn.get_actor_location()}')
    pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Pawn)
    print(f'Total pawns in PIE: {len(pawns)}')
    for p in pawns:
        print(f'  pawn: {p.get_class().get_name()} controller={p.get_controller().get_name() if p.get_controller() else "NONE"}')
