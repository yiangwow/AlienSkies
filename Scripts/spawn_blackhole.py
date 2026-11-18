"""M87-style black hole, arena centerpiece (clean space):
- Event horizon: black sphere
- Photon ring: bright Fresnel rim
- Accretion disk: VOLUMETRIC point cloud (~130k fiery sprites) in swirling filament
  streams -> dense turbulent gas like M87 (same legit tech as the galaxy)
- Twin relativistic jets: bright beam + soft sheath
"""
import unreal, math, random

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
ml = unreal.MathLibrary

# EditorSphere = 3968 tris, base radius 160 (vs BasicShapes/Sphere 960 tris, r50). Smooth
# silhouette so the close-up core/photon-ring edge isn't visibly polygonal ("fake").
sphere = unreal.load_asset('/Engine/EditorMeshes/EditorSphere')
plane  = unreal.load_asset('/Engine/BasicShapes/Plane')
cone   = unreal.load_asset('/Engine/BasicShapes/Cone')
m_core = unreal.load_asset('/Game/AlienSkies/Materials/M_BlackHoleCore')
m_ring = unreal.load_asset('/Game/AlienSkies/Materials/M_PhotonRing')
m_jet  = unreal.load_asset('/Game/AlienSkies/Materials/M_Jet')
m_pt   = unreal.load_asset('/Game/AlienSkies/Materials/M_StarPoint')

for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('BlackHole_'):
        eas.destroy_actor(a)

CENTER = unreal.Vector(-620000, 0, 230000)
HOLE_R = 13000.0
# Apparent shadow/core radius — DECOUPLED from HOLE_R so the dark well can dominate
# ('source of the pull') without rescaling the disk/jets. Sized so the black void meets the
# disk's bright lensed inner ring with no dark gap, while staying small enough not to eat into
# the disk. Tuned via capture sweep (gap_22000/30000/38000 -> 32000 is the sweet spot). A larger
# black silhouette also covers the additive haze that was tinting the small core brown.
SHADOW_R = 32000.0

def add_hism(actor, name):
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    p = unreal.AddNewSubobjectParams(parent_handle=root,
        new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None)
    h, _ = sds.add_new_subobject(p)
    sds.rename_subobject(h, unreal.Text(name))
    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(
        unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    return unreal.HierarchicalInstancedStaticMeshComponent.cast(obj)

def spawn(label, mesh, mat, scale_vec, rot=unreal.Rotator(0,0,0), pos=None):
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, pos or CENTER, rot)
    a.set_actor_label(label); a.set_editor_property('is_spatially_loaded', False)
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_editor_property('static_mesh', mesh); smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_editor_property('cast_shadow', False); a.set_actor_scale3d(scale_vec)
    return a, smc.create_dynamic_material_instance(0, mat)

def lerp3(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)
def fire_color(t):
    if t < 0.16: return (1.0, 0.98, 0.92)
    if t < 0.45: return lerp3((1.0,0.92,0.7),(1.0,0.5,0.13),(t-0.16)/0.29)
    return lerp3((1.0,0.5,0.13),(0.8,0.12,0.03),(t-0.45)/0.55)

# 1) event horizon
cs = SHADOW_R/160.0   # EditorSphere base radius is 160
spawn('BlackHole_Core', sphere, m_core, unreal.Vector(cs,cs,cs))
# 2) photon ring
# Thin photon-ring rim hugging the core. NOTE: growing this to close the photon-ring<->disk gap
# (tried 1.375 ~44000) reads as a fake blown-out white donut — do NOT. The gap needs a softer,
# blended solution (smooth core mesh + softer rim + disk inner glow), not a fat Fresnel ring.
rs = (SHADOW_R*1.06)/160.0
spawn('BlackHole_PhotonRing', sphere, m_ring, unreal.Vector(rs,rs,rs))

# disk orientation (near edge-on 3/4)
to_cam=(1.0,0.0,0.10); _l=math.sqrt(sum(c*c for c in to_cam)); to_cam=tuple(c/_l for c in to_cam)
ax=(to_cam[1],-to_cam[0],0.0); _al=math.sqrt(sum(c*c for c in ax)) or 1.0; ax=tuple(c/_al for c in ax)
disk_normal = ml.rotate_angle_axis(unreal.Vector(*to_cam), 70.0, unreal.Vector(*ax))
disk_rot = ml.make_rot_from_z(disk_normal)
n = disk_normal

# 3) VOLUMETRIC accretion disk: swirling filament streams of fire sprites
disk_actor = eas.spawn_actor_from_class(unreal.Actor, CENTER, disk_rot)
disk_actor.set_actor_label('BlackHole_VolDisk'); disk_actor.set_editor_property('is_spatially_loaded', False)
hism = add_hism(disk_actor, 'DiskHISM')
hism.set_editor_property('static_mesh', plane)
hism.set_editor_property('num_custom_data_floats', 3); hism.set_editor_property('cast_shadow', False)
disk_mid = hism.create_dynamic_material_instance(0, m_pt)
disk_mid.set_scalar_parameter_value('Brightness', 3.2)   # lower than galaxy(9) so fire colors show, not white

rng = random.Random(11)
innerR = HOLE_R*1.5; outerR = HOLE_R*6.0
N = 130000; STREAMS = 90; TWIST = 9.0
tfm=[]; cols=[]
for i in range(N):
    rr = rng.random()**0.6                          # concentrate toward inner (hotter, denser)
    r = innerR + (outerR-innerR)*rr
    if rng.random() < 0.8:                          # 80% in tight filament streams
        s = rng.randrange(STREAMS)
        theta = s*(2*math.pi/STREAMS) + (r/outerR)*TWIST + rng.gauss(0, 0.05)
    else:                                           # 20% diffuse fill
        theta = rng.uniform(0, 2*math.pi)
    th_frac = r/outerR
    z = rng.gauss(0,1.0) * HOLE_R*0.10 * (1.0 - 0.5*th_frac)   # thin, thicker inner
    x = r*math.cos(theta); y = r*math.sin(theta)
    sz = (90.0 + rng.random()*230.0)/50.0
    tfm.append(unreal.Transform(unreal.Vector(x,y,z), unreal.Rotator(0,0,0), unreal.Vector(sz,sz,sz)))
    c = fire_color(th_frac)
    # brighter inner; relativistic beaming (approaching side brighter)
    beam = 0.55 + 0.6*math.cos(theta)
    b = rng.uniform(0.30,0.95) * (1.5 - 0.8*th_frac) * beam
    cols.append((c[0]*b, c[1]*b, c[2]*b))
hism.add_instances(tfm, False, False)
last=len(cols)-1
for idx,c in enumerate(cols):
    hism.set_custom_data_value(idx,0,c[0],False); hism.set_custom_data_value(idx,1,c[1],False)
    hism.set_custom_data_value(idx,2,c[2], idx==last)
print(f'VolDisk: {hism.get_instance_count()} fire sprites')

# 4) jets
JET_LEN=560.0; half=50.0*JET_LEN
for sgn,tag in ((1.0,'N'),(-1.0,'S')):
    axis=unreal.Vector(n.x*sgn,n.y*sgn,n.z*sgn); rot=ml.make_rot_from_z(axis)
    pos=unreal.Vector(CENTER.x+axis.x*half, CENTER.y+axis.y*half, CENTER.z+axis.z*half)
    _,jm=spawn(f'BlackHole_Jet{tag}', cone, m_jet, unreal.Vector(9.0,9.0,JET_LEN), rot, pos=pos)
    jm.set_scalar_parameter_value('Brightness',26.0)
    _,sm=spawn(f'BlackHole_JetSheath{tag}', cone, m_jet, unreal.Vector(30.0,30.0,JET_LEN*0.9), rot, pos=pos)
    sm.set_scalar_parameter_value('Brightness',6.0)

# frame
cam=unreal.Vector(CENTER.x+150000, CENTER.y, CENTER.z+20000)
d=unreal.Vector(CENTER.x-cam.x,CENTER.y-cam.y,CENTER.z-cam.z)
yaw=math.degrees(math.atan2(d.y,d.x)); pitch=math.degrees(math.atan2(d.z,math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0,pitch,yaw))
les.editor_invalidate_viewports(); saved=les.save_current_level()
print(f'Volumetric M87 black hole assembled. Saved: {saved}')
