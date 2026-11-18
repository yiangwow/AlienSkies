"""Apply gap + haze fixes and verify.
- Core sphere + photon ring -> 48000 (covers the ~44k lensed apparent shadow -> no dark gap).
- CaptureR stays 34000 (< core, so the opaque ball covers the captured region).
- Corona already rebuilt with InnerR=36000 (haze fills down near the shadow).
Captures: fix_gap (D=140000, gap check) + fix_haze_close (D=45000, haze-up-close check).
"""
import unreal, math, os

CENTER = unreal.Vector(-620000, 0, 230000)
CORE_R = 48000.0
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

core = ring = disk = None
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl == 'BlackHole_Core': core = a
    elif lbl == 'BlackHole_PhotonRing': ring = a
    elif lbl == 'BlackHole_RMDisk': disk = a
core.set_actor_scale3d(unreal.Vector(CORE_R/50.0, CORE_R/50.0, CORE_R/50.0))
ring.set_actor_scale3d(unreal.Vector(CORE_R*1.08/50.0, CORE_R*1.08/50.0, CORE_R*1.08/50.0))
disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0).set_scalar_parameter_value('CaptureR', 34000.0)
les.save_current_level()

to_cam = (1.0, 0.0, 0.10); _l = math.sqrt(sum(c*c for c in to_cam)); to_cam = tuple(c/_l for c in to_cam)
ax = (to_cam[1], -to_cam[0], 0.0); _al = math.sqrt(sum(c*c for c in ax)) or 1.0; ax = tuple(c/_al for c in ax)
N = ml.rotate_angle_axis(unreal.Vector(*to_cam), 52.0, unreal.Vector(*ax))
def norm(v):
    L = math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L, v.y/L, v.z/L)
def cross(a, b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
perp = norm(cross(N, unreal.Vector(0, 0, 1)))
e = math.radians(14.0)
cdir = norm(unreal.Vector(perp.x*math.cos(e)+N.x*math.sin(e), perp.y*math.cos(e)+N.y*math.sin(e), perp.z*math.cos(e)+N.z*math.sin(e)))

for name, D, fov in [('fix_gap', 140000.0, 70.0), ('fix_haze_close', 45000.0, 75.0)]:
    cam = unreal.Vector(CENTER.x+cdir.x*D, CENTER.y+cdir.y*D, CENTER.z+cdir.z*D)
    rot = ml.find_look_at_rotation(cam, CENTER)
    ues.set_level_viewport_camera_info(cam, rot)
    path = f'{OUT}/{name}.png'
    if os.path.exists(path):
        try: os.remove(path)
        except Exception: pass
    rt = unreal.TextureRenderTarget2D()
    rt.set_editor_property('size_x', 1280); rt.set_editor_property('size_y', 720)
    rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    ca = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    try:
        cap = ca.capture_component2d
        cap.set_editor_property('texture_target', rt)
        cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cap.set_editor_property('fov_angle', fov)
        cap.set_editor_property('capture_every_frame', False)
        cap.set_editor_property('capture_on_movement', False)
        cap.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{name}.png')
    finally:
        eas.destroy_actor(ca)
    print(f'{name}: D={D}')
print('Done. core/ring=48000, CaptureR=34000, corona InnerR=36000.')
