import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
v=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='VolGalaxy_Hero': v=a; break
# flatten disc to XY plane so we can view face-on
v.set_actor_rotation(unreal.Rotator(0,0,0), False)
C=v.get_actor_location()
# camera above + offset for a 3/4 face view
cam=unreal.Vector(C.x+90000, C.y+30000, C.z+240000)
d=unreal.Vector(C.x-cam.x,C.y-cam.y,C.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('face-on view')
