"""CaptureR didn't cover the polar background leak. Grow the OPAQUE core (EditorSphere, base
radius 160) to fill out to the bright ring -> blocks the background. Reset CaptureR=34000.
Sweep core size; framing like #25. Background-leak visible offline."""
import unreal, math, os
CENTER = unreal.Vector(-620000, 0, 230000)
OUT = 'E:/projects/AlienSkies/Screenshots'
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')
core = disk = ring = None
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl=='BlackHole_Core': core=a
    elif lbl=='BlackHole_RMDisk': disk=a
    elif lbl=='BlackHole_PhotonRing': ring=a
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_scalar_parameter_value('CaptureR', 34000.0)
def matched_pp():
    pp = unreal.PostProcessSettings()
    pp.set_editor_property('override_auto_exposure_method', True)
    pp.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property('override_auto_exposure_bias', True); pp.set_editor_property('auto_exposure_bias', 11.0)
    pp.set_editor_property('override_auto_exposure_min_brightness', True); pp.set_editor_property('auto_exposure_min_brightness', 1.0)
    pp.set_editor_property('override_auto_exposure_max_brightness', True); pp.set_editor_property('auto_exposure_max_brightness', 1.0)
    return pp
cam = unreal.Vector(CENTER.x + 175000, CENTER.y, CENTER.z + 30000)
rot = ml.find_look_at_rotation(cam, CENTER)
ues.set_level_viewport_camera_info(cam, rot)
for R in [55000.0, 72000.0, 90000.0]:
    s = R/160.0
    core.set_actor_scale3d(unreal.Vector(s,s,s))
    # keep photon ring just outside the core so it still reads as the rim
    rs = (R*1.04)/160.0
    ring.set_actor_scale3d(unreal.Vector(rs,rs,rs))
    nm = f'corefill_{int(R/1000)}k'
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
    cap.set_editor_property('fov_angle', 72.0)
    cap.set_editor_property('capture_every_frame', False)
    cap.set_editor_property('capture_on_movement', False)
    cap.set_editor_property('post_process_settings', matched_pp())
    cap.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{nm}.png')
    eas.destroy_actor(ca)
    print(nm)
print('Done.')
