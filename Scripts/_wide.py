import unreal
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(50000,0,40000), unreal.Rotator(0.0,-5.0,180.0))
les.editor_invalidate_viewports(); print('wide view')
