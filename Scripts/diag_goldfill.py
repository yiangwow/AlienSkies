"""Pinpoint the gold-center-at-distance: capture at a FAR framing (like image #14) with
(a) everything, (b) corona hidden, (c) disk hidden. Whichever removal makes the center go
black is the culprit. Exposure-matched (note: SceneCapture under-blooms vs Standalone)."""
import unreal, math, os
CENTER = unreal.Vector(-620000, 0, 230000)
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')
corona = disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_InfallCorona': corona = a
    elif a.get_actor_label() == 'BlackHole_RMDisk': disk = a
def matched_pp():
    pp = unreal.PostProcessSettings()
    pp.set_editor_property('override_auto_exposure_method', True)
    pp.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property('override_auto_exposure_bias', True)
    pp.set_editor_property('auto_exposure_bias', 11.0)
    pp.set_editor_property('override_auto_exposure_min_brightness', True)
    pp.set_editor_property('auto_exposure_min_brightness', 1.0)
    pp.set_editor_property('override_auto_exposure_max_brightness', True)
    pp.set_editor_property('auto_exposure_max_brightness', 1.0)
    return pp
to_cam = (1.0, 0.0, 0.10); _l = math.sqrt(sum(c*c for c in to_cam)); to_cam = tuple(c/_l for c in to_cam)
ax = (to_cam[1], -to_cam[0], 0.0); _al = math.sqrt(sum(c*c for c in ax)) or 1.0; ax = tuple(c/_al for c in ax)
N = ml.rotate_angle_axis(unreal.Vector(*to_cam), 52.0, unreal.Vector(*ax))
def norm(v):
    L = math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L, v.y/L, v.z/L)
def cross(a, b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
perp = norm(cross(N, unreal.Vector(0, 0, 1)))
e = math.radians(16.0)
cdir = norm(unreal.Vector(perp.x*math.cos(e)+N.x*math.sin(e), perp.y*math.cos(e)+N.y*math.sin(e), perp.z*math.cos(e)+N.z*math.sin(e)))
D = 230000.0
cam = unreal.Vector(CENTER.x+cdir.x*D, CENTER.y+cdir.y*D, CENTER.z+cdir.z*D)
rot = ml.find_look_at_rotation(cam, CENTER)
ues.set_level_viewport_camera_info(cam, rot)
def shot(nm):
    path=f'{OUT}/{nm}.png'
    if os.path.exists(path):
        try: os.remove(path)
        except Exception: pass
    rt = unreal.TextureRenderTarget2D()
    rt.set_editor_property('size_x', 1280); rt.set_editor_property('size_y', 720)
    rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    ca = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cap = ca.capture_component2d
    cap.set_editor_property('texture_target', rt)
    cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('fov_angle', 70.0)
    cap.set_editor_property('capture_every_frame', False)
    cap.set_editor_property('capture_on_movement', False)
    cap.set_editor_property('post_process_settings', matched_pp())
    cap.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{nm}.png')
    eas.destroy_actor(ca)
    print(nm)
shot('gold_all')
corona.set_actor_hidden_in_game(True); ues.get_editor_subsystem  # noop
corona.set_editor_property('hidden', True)
shot('gold_nocorona')
corona.set_editor_property('hidden', False)
disk.set_editor_property('hidden', True)
shot('gold_nodisk')
disk.set_editor_property('hidden', False)
print('Done. restored visibility.')
