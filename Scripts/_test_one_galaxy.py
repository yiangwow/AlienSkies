import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml=unreal.MathLibrary
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
gal=unreal.load_asset('/Game/AlienSkies/Materials/M_SpiralGalaxy')
# remove old test
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='TEST_Galaxy': eas.destroy_actor(a)
# place one isolated galaxy far above everything, facing a camera we control
C=unreal.Vector(0,0,800000)
a=eas.spawn_actor_from_class(unreal.StaticMeshActor,C,unreal.Rotator(0,0,0))
a.set_actor_label('TEST_Galaxy'); a.set_editor_property('is_spatially_loaded',False)
smc=a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_editor_property('static_mesh',plane); smc.set_mobility(unreal.ComponentMobility.MOVABLE)
smc.set_editor_property('cast_shadow',False)
sc=3000; a.set_actor_scale3d(unreal.Vector(sc,sc,sc))
# face camera (camera will be at +X from it), tilt 30 for near face-on
to_cam=(1.0,0.0,0.0)
normal=ml.rotate_angle_axis(unreal.Vector(*to_cam),30.0,unreal.Vector(0,1,0))
a.set_actor_rotation(ml.make_rot_from_z(normal),False)
mid=smc.create_dynamic_material_instance(0,gal)
mid.set_scalar_parameter_value('ArmCount',2.0); mid.set_scalar_parameter_value('SpinTightness',5.0)
mid.set_scalar_parameter_value('Brightness',7.0)
mid.set_vector_parameter_value('CoreColor',unreal.LinearColor(0.9,0.85,1.0,1.0))
mid.set_vector_parameter_value('ArmColor',unreal.LinearColor(0.7,0.5,1.0,1.0))
mid.set_scalar_parameter_value('RotationSpeed',0.0)
# camera: face-on-ish, framed so galaxy fills ~70%
cam=unreal.Vector(C.x+520000,C.y,C.z+30000)
d=unreal.Vector(C.x-cam.x,C.y-cam.y,C.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); print('isolated test galaxy placed + framed')
