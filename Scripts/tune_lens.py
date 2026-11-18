"""Sweep LensStrength on BlackHole_RMDisk and capture at 10deg edge-on each time, so we
can pick where the gravitational wrap reads best. MID-param only (no recompile).
Outputs: Screenshots/lens_s<val>.png
"""
import unreal, math, os

CENTER = unreal.Vector(-620000, 0, 230000)
D = 260000.0
STRENGTHS = [9000.0, 16000.0, 26000.0]
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_RMDisk':
        disk = a; break
smc = disk.get_component_by_class(unreal.StaticMeshComponent)
mid = smc.get_material(0)

# 10deg edge-on camera (same derivation as cap_lensing.py)
to_cam = (1.0, 0.0, 0.10); _l = math.sqrt(sum(c*c for c in to_cam)); to_cam = tuple(c/_l for c in to_cam)
ax = (to_cam[1], -to_cam[0], 0.0); _al = math.sqrt(sum(c*c for c in ax)) or 1.0; ax = tuple(c/_al for c in ax)
N = ml.rotate_angle_axis(unreal.Vector(*to_cam), 52.0, unreal.Vector(*ax))
def norm(v):
    L = math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L, v.y/L, v.z/L)
def cross(a, b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
perp = norm(cross(N, unreal.Vector(0, 0, 1)))
e = math.radians(10.0)
cdir = norm(unreal.Vector(perp.x*math.cos(e)+N.x*math.sin(e),
                          perp.y*math.cos(e)+N.y*math.sin(e),
                          perp.z*math.cos(e)+N.z*math.sin(e)))
cam = unreal.Vector(CENTER.x+cdir.x*D, CENTER.y+cdir.y*D, CENTER.z+cdir.z*D)
rot = ml.find_look_at_rotation(cam, CENTER)
ues.set_level_viewport_camera_info(cam, rot)

for strength in STRENGTHS:
    mid.set_scalar_parameter_value('LensStrength', strength)
    name = f'lens_s{int(strength)}'
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
    print(f'{name}: LensStrength={strength}')
print('Done.')
