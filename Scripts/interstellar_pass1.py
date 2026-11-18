"""Interstellar pass 1: re-orient disk to near edge-on (vertical normal), kill the frame-filling
corona haze, hide jets. Live param updates (box bounds any orientation). Capture edge-on."""
import unreal, math, os
CENTER = unreal.Vector(-620000, 0, 230000)
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')
def norm(v):
    L=math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L,v.y/L,v.z/L)
def cross(a,b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
# Near-vertical disk normal (slight tilt toward +X) -> horizontal edge-on disk like Gargantua
N = norm(unreal.Vector(0.20, 0.0, 1.0))
upref = unreal.Vector(1,0,0) if abs(N.z)>0.9 else unreal.Vector(0,0,1)
U = norm(cross(upref, N)); V = norm(cross(N, U))
disk = corona = None
jets = []
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl == 'BlackHole_RMDisk': disk = a
    elif lbl == 'BlackHole_InfallCorona': corona = a
    elif lbl.startswith('BlackHole_Jet'): jets.append(a)
# disk orientation
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_vector_parameter_value('DiskN', unreal.LinearColor(N.x,N.y,N.z,0))
dm.set_vector_parameter_value('DiskU', unreal.LinearColor(U.x,U.y,U.z,0))
dm.set_vector_parameter_value('DiskV', unreal.LinearColor(V.x,V.y,V.z,0))
# corona: nearly off (faint), matched orientation
cm = corona.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
cm.set_scalar_parameter_value('Brightness', 0.02)
cm.set_vector_parameter_value('DiskN', unreal.LinearColor(N.x,N.y,N.z,0))
cm.set_vector_parameter_value('DiskU', unreal.LinearColor(U.x,U.y,U.z,0))
cm.set_vector_parameter_value('DiskV', unreal.LinearColor(V.x,V.y,V.z,0))
# hide jets (reference has none)
for j in jets: j.set_editor_property('hidden', True)
les.save_current_level()
print(f'N={N.x:.2f},{N.y:.2f},{N.z:.2f}; jets hidden={len(jets)}; corona Brightness=0.02')

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
# edge-on framing: camera in the disk plane (slight elevation above it)
for nm, D, elev in [('is1_wide', 200000.0, 0.16), ('is1_mid', 130000.0, 0.13)]:
    cam = unreal.Vector(CENTER.x + D, CENTER.y, CENTER.z + D*elev)
    rot = ml.find_look_at_rotation(cam, CENTER)
    ues.set_level_viewport_camera_info(cam, rot)
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
print('Done.')
