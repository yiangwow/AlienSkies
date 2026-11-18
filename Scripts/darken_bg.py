"""Rebuild M_StarDome (now with DomeBrightness knob), re-apply to SM_SkySphere as a MID,
dial background dark, capture to compare a few darkness levels."""
import unreal, math, os, subprocess
# 1) rebuild the material with the new knob
exec(open('E:/projects/AlienSkies/Scripts/build_stardome_material.py').read())
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')
star_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarDome')
sky = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'SM_SkySphere': sky = a
smc = sky.get_component_by_class(unreal.StaticMeshComponent)
mid = smc.create_dynamic_material_instance(0, star_mat)
CENTER = unreal.Vector(-620000, 0, 230000)
OUT = 'E:/projects/AlienSkies/Screenshots'
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
cam = unreal.Vector(CENTER.x + 165000, CENTER.y, CENTER.z + 9000)
rot = ml.find_look_at_rotation(cam, CENTER)
ues.set_level_viewport_camera_info(cam, rot)
for val in [0.30, 0.15, 0.06]:
    mid.set_scalar_parameter_value('DomeBrightness', val)
    nm = f'bg_{int(val*100)}'
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
mid.set_scalar_parameter_value('DomeBrightness', 0.15)
les.save_current_level()
print('Saved with DomeBrightness=0.15')
