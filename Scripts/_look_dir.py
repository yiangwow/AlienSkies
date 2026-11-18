import unreal, sys
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(0,0,10000), unreal.Rotator(0.0, -88.0, 0.0))
les.editor_invalidate_viewports()
print('looking down')
