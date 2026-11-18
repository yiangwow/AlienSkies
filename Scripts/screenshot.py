"""Just take a screenshot. No sky tuning. SceneCapture2D path, ~1.3s.
Output: E:/projects/AlienSkies/Screenshots/iter.png
"""
import unreal
import os

SCREENSHOT_DIR = 'E:/projects/AlienSkies/Screenshots'
SCREENSHOT_PATH = f'{SCREENSHOT_DIR}/iter.png'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Keep editor ticking even when not focused
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
editor_world = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(editor_world, 'Slate.bAllowThrottling 0')

if os.path.exists(SCREENSHOT_PATH):
    try: os.remove(SCREENSHOT_PATH)
    except Exception: pass

cam_loc, cam_rot = ues.get_level_viewport_camera_info()

rt = unreal.TextureRenderTarget2D()
rt.set_editor_property('size_x', 1280)
rt.set_editor_property('size_y', 720)
rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
capture_actor = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, cam_rot)
try:
    cap = capture_actor.capture_component2d
    cap.set_editor_property('texture_target', rt)
    cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('fov_angle', 90.0)
    cap.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('capture_every_frame', False)
    cap.set_editor_property('capture_on_movement', False)
    # NOTE: SceneCapture2D cannot render post-process MATERIALS that remap scene UVs
    # (PostProcessInput0 is bound to the current pixel only), so we do NOT attach the
    # PP lensing here — it would not show. PP materials only render in the editor
    # viewport / PIE. See the 2026-05-31 diary entry on the lensing tooling wall.
    cap.capture_scene()
    unreal.RenderingLibrary.export_render_target(editor_world, rt, SCREENSHOT_DIR, 'iter.png')
finally:
    eas.destroy_actor(capture_actor)

print(f'Screenshot -> {SCREENSHOT_PATH}')
