import unreal, math
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
C=unreal.Vector(-620000,0,230000)
cam=unreal.Vector(C.x+95000, C.y, C.z+14000)
d=unreal.Vector(C.x-cam.x,C.y-cam.y,C.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('close BH')
