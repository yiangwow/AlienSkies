import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# move volumetric galaxy to clean empty space, away from billboards
NEW=unreal.Vector(0,0,900000)
v=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='VolGalaxy_Hero': v=a; break
v.set_actor_location(NEW,False,False)
# frame it from ~250k, slight above for a 3/4 read
cam=unreal.Vector(NEW.x+250000, NEW.y, NEW.z+70000)
d=unreal.Vector(NEW.x-cam.x,NEW.y-cam.y,NEW.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('isolated volumetric galaxy')
