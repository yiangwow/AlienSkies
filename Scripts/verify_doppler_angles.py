"""Verify the view-dependent Doppler crescent: orbit the editor camera around the
black hole and SceneCapture from 3 azimuths. If Doppler is view-dependent (Version B),
the bright crescent should face the camera in EVERY shot.
Outputs: Screenshots/dop_a.png, dop_b.png, dop_c.png
"""
import unreal, math, os

CENTER = unreal.Vector(-620000, 0, 230000)
R = 280000.0      # horizontal orbit radius (disk outer = 80k, so well outside)
ZELEV = 120000.0  # elevation so the disk reads as a tilted ellipse, not edge-on
SHOTS = [('dop_a', 0.0), ('dop_b', 120.0), ('dop_c', 240.0)]

OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

for name, az in SHOTS:
    rad = math.radians(az)
    cam = unreal.Vector(CENTER.x + R*math.cos(rad), CENTER.y + R*math.sin(rad), CENTER.z + ZELEV)
    rot = ml.find_look_at_rotation(cam, CENTER)
    ues.set_level_viewport_camera_info(cam, rot)

    path = f'{OUT}/{name}.png'
    if os.path.exists(path):
        try: os.remove(path)
        except Exception: pass

    rt = unreal.TextureRenderTarget2D()
    rt.set_editor_property('size_x', 1280)
    rt.set_editor_property('size_y', 720)
    rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)

    cap_actor = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    try:
        cap = cap_actor.capture_component2d
        cap.set_editor_property('texture_target', rt)
        cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cap.set_editor_property('fov_angle', 60.0)
        cap.set_editor_property('capture_every_frame', False)
        cap.set_editor_property('capture_on_movement', False)
        cap.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{name}.png')
    finally:
        eas.destroy_actor(cap_actor)
    print(f'{name}: az={az} cam=({cam.x:.0f},{cam.y:.0f},{cam.z:.0f})')

print('Done. 3 orbit shots captured.')
