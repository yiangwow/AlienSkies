"""Reproduce the corona-haze-disappears bug. CORONA_R = 390000.
Capture from OUTSIDE the sphere (haze should be present) and INSIDE (should vanish).
Outputs: Screenshots/corona_far.png, corona_near.png
"""
import unreal, os

CENTER = unreal.Vector(-620000, 0, 230000)
CORONA_R = 390000.0
OUT = 'E:/projects/AlienSkies/Screenshots'
os.makedirs(OUT, exist_ok=True)

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ml = unreal.MathLibrary
world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')

# (name, distance-from-center along +X with slight +Z)
SHOTS = [('corona_far', 650000.0), ('corona_near', 180000.0)]

for name, dist in SHOTS:
    cam = unreal.Vector(CENTER.x + dist, CENTER.y, CENTER.z + dist * 0.25)
    d_from_center = ((cam.x-CENTER.x)**2 + (cam.y-CENTER.y)**2 + (cam.z-CENTER.z)**2) ** 0.5
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
        cap.set_editor_property('fov_angle', 70.0)
        cap.set_editor_property('capture_every_frame', False)
        cap.set_editor_property('capture_on_movement', False)
        cap.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, OUT, f'{name}.png')
    finally:
        eas.destroy_actor(ca)
    inside = 'INSIDE' if d_from_center < CORONA_R else 'OUTSIDE'
    print(f'{name}: dist_from_center={d_from_center:.0f} ({inside} corona R={CORONA_R:.0f})')

print('Done.')
