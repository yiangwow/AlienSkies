"""Capture CURRENT (reverted/default) look, then apply the full Interstellar param set
IN MEMORY (no save), capture again at the same two cameras. Lets the user pick which look
to keep before anything is committed. Offline SceneCapture under-blooms -> judge gross
differences (dark vs bright bg, edge-on vs tilted disk, void size), not final glow."""
import unreal, os
CENTER = unreal.Vector(-620000, 0, 230000)
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

def find(lbl):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lbl:
            return a
    return None

core = find('BlackHole_Core'); ring = find('BlackHole_PhotonRing')
disk = find('BlackHole_RMDisk'); sky = find('SM_SkySphere')
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
sm = sky.get_component_by_class(unreal.StaticMeshComponent).get_material(0)

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

CAMS = [
    ('edge',  unreal.Vector(CENTER.x + 150000, CENTER.y, CENTER.z + 9000),  70.0),
    ('above', unreal.Vector(CENTER.x + 210000, CENTER.y, CENTER.z + 90000), 70.0),
]

def shoot(tag):
    for cnm, cam, fov in CAMS:
        rot = ml.find_look_at_rotation(cam, CENTER)
        ues.set_level_viewport_camera_info(cam, rot)
        nm = f'cmp_{tag}_{cnm}'
        path = f'{OUT}/{nm}.png'
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
        cap.set_editor_property('fov_angle', fov)
        cap.set_editor_property('capture_every_frame', False)
        cap.set_editor_property('capture_on_movement', False)
        cap.set_editor_property('post_process_settings', matched_pp())
        cap.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{nm}.png')
        eas.destroy_actor(ca)
        print('shot', nm)

# ---- 1) CURRENT look ----
shoot('current')

# ---- 2) Apply Interstellar params IN MEMORY (no save) ----
R = 90000.0
core.set_actor_scale3d(unreal.Vector(R/160.0, R/160.0, R/160.0))
ring.set_actor_scale3d(unreal.Vector(R*1.04/160.0, R*1.04/160.0, R*1.04/160.0))
# edge-on: disk plane normal vertical -> Gargantua wrap over/under
dm.set_vector_parameter_value('DiskN', unreal.LinearColor(0, 0, 1, 0))
dm.set_vector_parameter_value('DiskU', unreal.LinearColor(1, 0, 0, 0))
dm.set_vector_parameter_value('DiskV', unreal.LinearColor(0, 1, 0, 0))
dm.set_scalar_parameter_value('InnerR', 20000.0)
dm.set_scalar_parameter_value('OuterR', 150000.0)
dm.set_scalar_parameter_value('BoundR', 200000.0)
dm.set_scalar_parameter_value('Thickness', 9000.0)
dm.set_scalar_parameter_value('Brightness', 2.6)
dm.set_scalar_parameter_value('LensStrength', 40000.0)
dm.set_scalar_parameter_value('CaptureR', 34000.0)
sc = (200000.0 * 2.1) / 100.0
disk.set_actor_scale3d(unreal.Vector(sc, sc, sc))
sm.set_scalar_parameter_value('DomeBrightness', 0.09)
print('Interstellar params applied in-memory (NOT saved).')

shoot('inter')
print('Done. NOT saved -> level still on current/default look on disk.')
