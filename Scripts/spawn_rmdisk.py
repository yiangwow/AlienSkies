"""Replace the black hole's disk with the raymarched volumetric box disk.
Keeps the existing core / photon ring / jets from spawn_blackhole.py.
"""
import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml=unreal.MathLibrary
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
m_rm=unreal.load_asset('/Game/AlienSkies/Materials/M_RaymarchDisk')

CENTER=unreal.Vector(-620000,0,230000); HOLE_R=13000.0
INNER=HOLE_R*1.5; OUTER=HOLE_R*6.0; THICK=HOLE_R*0.42

# remove old disks
for a in eas.get_all_level_actors():
    if a.get_actor_label() in ('BlackHole_VolDisk','BlackHole_RMDisk'):
        eas.destroy_actor(a)

# disk basis (same tilt as before)
to_cam=(1.0,0.0,0.10); _l=math.sqrt(sum(c*c for c in to_cam)); to_cam=tuple(c/_l for c in to_cam)
ax=(to_cam[1],-to_cam[0],0.0); _al=math.sqrt(sum(c*c for c in ax)) or 1.0; ax=tuple(c/_al for c in ax)
N=ml.rotate_angle_axis(unreal.Vector(*to_cam),52.0,unreal.Vector(*ax))
disk_rot=ml.make_rot_from_z(N)
# in-plane basis
U=ml.rotate_angle_axis(unreal.Vector(1,0,0),0.0,N)  # placeholder; compute robust perp below
# robust U perpendicular to N
upref=unreal.Vector(0,0,1)
if abs(N.z)>0.9: upref=unreal.Vector(1,0,0)
def cross(a,b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
def norm(v):
    L=math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L,v.y/L,v.z/L)
U=norm(cross(upref,N)); V=norm(cross(N,U))

# spawn box
a=eas.spawn_actor_from_class(unreal.StaticMeshActor, CENTER, disk_rot)
a.set_actor_label('BlackHole_RMDisk'); a.set_editor_property('is_spatially_loaded',False)
smc=a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_editor_property('static_mesh',cube); smc.set_mobility(unreal.ComponentMobility.MOVABLE)
smc.set_editor_property('cast_shadow',False)
# Near-cube box: lensing bends the disk's far side UP/DOWN over the shadow, so the box
# must enclose a bounding sphere of radius BOUND (not just the thin disk slab) — else the
# wrapped image is clipped to the old slab silhouette.
BOUND=OUTER*1.5
sxy=(BOUND*2.1)/100.0; sz=(BOUND*2.1)/100.0
a.set_actor_scale3d(unreal.Vector(sxy,sxy,sz))
mid=smc.create_dynamic_material_instance(0,m_rm)
mid.set_scalar_parameter_value('InnerR',INNER)
mid.set_scalar_parameter_value('OuterR',OUTER)
mid.set_scalar_parameter_value('Thickness',THICK)
mid.set_scalar_parameter_value('Spin',0.3)
mid.set_scalar_parameter_value('Brightness',0.7)
mid.set_vector_parameter_value('DiskN',unreal.LinearColor(N.x,N.y,N.z,0))
mid.set_vector_parameter_value('DiskU',unreal.LinearColor(U.x,U.y,U.z,0))
mid.set_vector_parameter_value('DiskV',unreal.LinearColor(V.x,V.y,V.z,0))
mid.set_scalar_parameter_value('BoundR',BOUND)
mid.set_scalar_parameter_value('LensStrength',16000.0)
mid.set_scalar_parameter_value('CaptureR',15000.0)  # INTENTIONALLY below InnerR(19500) & core
# (32000): the additive disk renders IN FRONT of the opaque core, so letting all the bright inner
# gas (InnerR..) accumulate makes the ring HUG the core tight with no dark gap. Raising CaptureR
# above InnerR cuts that inner band and opens a brown gap (regression we hit). Keep at ~15000.

# frame
cam=unreal.Vector(CENTER.x+170000, CENTER.y, CENTER.z+24000)
d=unreal.Vector(CENTER.x-cam.x,CENTER.y-cam.y,CENTER.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam,unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); les.save_current_level()
print(f'Raymarch disk box spawned. N={N.x:.2f},{N.y:.2f},{N.z:.2f}')
