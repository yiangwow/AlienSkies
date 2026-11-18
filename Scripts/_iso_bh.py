import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# hide all galaxies (billboard + volumetric) so we can see the black hole alone
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l.startswith('Galaxy_') or l.startswith('VolGalaxy'):
        a.set_is_temporarily_hidden_in_editor(True)
# frame the black hole
C=unreal.Vector(-260000,0,150000)
cam=unreal.Vector(C.x+150000, C.y, C.z+20000)
d=unreal.Vector(C.x-cam.x,C.y-cam.y,C.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('isolated black hole')
