import unreal, math
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tp=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='Galaxy_Hero': tp=a.get_actor_location(); break
# Galaxy ~340k across; sit ~330k away along +X for a good framing
cam = unreal.Vector(tp.x+330000, tp.y, tp.z+40000)
d = unreal.Vector(tp.x-cam.x, tp.y-cam.y, tp.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('framed hero from 330k')
