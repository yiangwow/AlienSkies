"""Capture from the camera PAWN's POV (its CameraComponent world transform) so the attached
viewmodel appears in frame. Exports Screenshots/fp_mech.png."""
import unreal, os
OUT = 'E:/projects/AlienSkies/Screenshots'
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

loc, rot = unreal.Vector(0, 0, 10000), unreal.Rotator(0, 180, 0)
for a in eas.get_all_level_actors():
    cc = a.get_component_by_class(unreal.CameraComponent)
    if cc:
        loc, rot = cc.get_world_location(), cc.get_world_rotation()
        break

def matched_pp():
    pp = unreal.PostProcessSettings()
    for k, v in [('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL),
                 ('auto_exposure_bias', 11.0), ('auto_exposure_min_brightness', 1.0),
                 ('auto_exposure_max_brightness', 1.0)]:
        pp.set_editor_property('override_' + k, True); pp.set_editor_property(k, v)
    return pp

nm = 'fp_mech'
p = f'{OUT}/{nm}.png'
if os.path.exists(p):
    try: os.remove(p)
    except Exception: pass
rt = unreal.TextureRenderTarget2D()
rt.set_editor_property('size_x', 1280); rt.set_editor_property('size_y', 720)
rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
ca = eas.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
cap = ca.capture_component2d
cap.set_editor_property('texture_target', rt)
cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
cap.set_editor_property('fov_angle', 90.0)
cap.set_editor_property('capture_every_frame', False)
cap.set_editor_property('capture_on_movement', False)
cap.set_editor_property('post_process_settings', matched_pp())
cap.capture_scene()
unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{nm}.png')
eas.destroy_actor(ca)
print('shot', nm, 'from', f'({loc.x:.0f},{loc.y:.0f},{loc.z:.0f})')
