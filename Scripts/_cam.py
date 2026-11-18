import unreal, sys
yaw = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(0,0,10000), unreal.Rotator(0.0, 0.0, yaw))
les.editor_invalidate_viewports()
print(f'cam yaw={yaw}')
