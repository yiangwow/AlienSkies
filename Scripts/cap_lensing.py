"""Capture the lensed disk from near-edge-on angles (where the gravitational wrap over
the shadow is most visible). Computes the disk normal N the same way spawn_rmdisk.py does,
then places cameras at small elevations above the disk plane, looking at the hole.
Outputs: Screenshots/lens_10.png (10deg), lens_28.png (28deg)
"""
import unreal, math, os

CENTER = unreal.Vector(-620000, 0, 230000)
D = 260000.0
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

# disk normal N (identical derivation to spawn_rmdisk.py)
to_cam = (1.0, 0.0, 0.10); _l = math.sqrt(sum(c*c for c in to_cam)); to_cam = tuple(c/_l for c in to_cam)
ax = (to_cam[1], -to_cam[0], 0.0); _al = math.sqrt(sum(c*c for c in ax)) or 1.0; ax = tuple(c/_al for c in ax)
N = ml.rotate_angle_axis(unreal.Vector(*to_cam), 52.0, unreal.Vector(*ax))
def norm(v):
    L = math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L, v.y/L, v.z/L)
def cross(a, b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
perp = norm(cross(N, unreal.Vector(0, 0, 1)))   # in-plane horizontal direction

for name, elev in [('lens_10', 10.0), ('lens_28', 28.0)]:
    e = math.radians(elev)
    cdir = norm(unreal.Vector(perp.x*math.cos(e)+N.x*math.sin(e),
                              perp.y*math.cos(e)+N.y*math.sin(e),
                              perp.z*math.cos(e)+N.z*math.sin(e)))
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
        cap.set_editor_property('fov_angle', 55.0)
        cap.set_editor_property('capture_every_frame', False)
        cap.set_editor_property('capture_on_movement', False)
        cap.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{name}.png')
    finally:
        eas.destroy_actor(ca)
    print(f'{name}: elev={elev}deg')
print('Done.')
