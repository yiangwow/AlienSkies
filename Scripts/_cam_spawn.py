import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# Exactly what the player sees on spawn: pos (0,0,10000), yaw 180 (BeginPlay), pitch 30
ues.set_level_viewport_camera_info(unreal.Vector(0,0,10000), unreal.Rotator(0.0, 30.0, 180.0))
les.editor_invalidate_viewports()
print('spawn view set (yaw 180, pitch 30)')
