import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
gw = ues.get_game_world()
if not gw:
    print('PIE not running')
else:
    pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Pawn)
    for p in pawns:
        before = p.get_editor_property('current_yaw')
        p.set_editor_property('target_yaw', 90.0)
        p.set_editor_property('target_pitch', 0.0)
        print(f'set target_yaw=90, target_pitch=0 (was current_yaw={before})')
        print('If Tick is alive, the view should now pan to face yaw 90.')
