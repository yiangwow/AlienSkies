"""Interstellar pass 2: darken background (MPC StarBrightness), brighten disk, and capture from
the DISK PLANE height to demonstrate the edge-on Gargantua look (vs the from-above ellipse)."""
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

# darken background
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
try:
    unreal.KismetMaterialLibrary.set_scalar_parameter_value(world, mpc, 'StarBrightness', 0.18)
    print('MPC StarBrightness -> 0.18')
except Exception as ex:
    print('MPC set failed:', ex)

# brighten disk
disk = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_RMDisk': disk = a
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_scalar_parameter_value('Brightness', 1.3)
les.save_current_level()
print('disk Brightness -> 1.3')

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

# camera AT the disk-plane height (Z = hole Z), horizontal -> edge-on; tiny Z offset to reveal wrap
for nm, D, dz in [('is2_edgeon', 165000.0, 9000.0), ('is2_close', 110000.0, 6000.0)]:
    cam = unreal.Vector(CENTER.x + D, CENTER.y, CENTER.z + dz)
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
