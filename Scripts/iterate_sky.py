"""
Apply sky parameter changes AND capture a screenshot of the active editor viewport
to a known path. Claude can read that screenshot directly without you uploading.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/iterate_sky.py"

Screenshot saves to:
    E:/projects/AlienSkies/Screenshots/iter.png
"""

import unreal
import os

SCREENSHOT_DIR = 'E:/projects/AlienSkies/Screenshots'
SCREENSHOT_PATH = f'{SCREENSHOT_DIR}/iter.png'

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def find_first_of_class(level_actors, cls):
    for a in level_actors:
        if a.get_class().get_name() == cls:
            return a
    return None


eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()

sky_atm = find_first_of_class(actors, 'SkyAtmosphere')
dir_light = find_first_of_class(actors, 'DirectionalLight')

# ---------- AGGRESSIVE PURPLE PUSH ----------
if sky_atm:
    comp = sky_atm.get_component_by_class(unreal.SkyAtmosphereComponent)
    if comp:
        # Even more violet-dominant. Reduce green to deepen the purple.
        comp.set_editor_property('rayleigh_scattering', unreal.LinearColor(0.10, 0.015, 1.8, 1.0))
        comp.set_editor_property('rayleigh_scattering_scale', 0.12)
        # Cut Mie hard — tight halo around sun only, not horizon-wide orange
        comp.set_editor_property('mie_scattering_scale', 0.0006)
        comp.set_editor_property('mie_anisotropy', 0.75)
        comp.set_editor_property('mie_scattering', unreal.LinearColor(0.8, 0.3, 0.1, 1.0))
        sky_atm.modify()

if dir_light:
    comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
    if comp:
        # Warmer white-ish spectrum so Rayleigh can scatter blue, keeping the sky purple
        comp.set_editor_property('use_temperature', True)
        comp.set_editor_property('temperature', 5000.0)  # daylight white
        comp.set_light_color(unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        comp.set_intensity(0.4)  # very dim
        # MUCH darker disc tint to kill the bright white hot-spot
        comp.set_editor_property('atmosphere_sun_disk_color_scale', unreal.LinearColor(0.25, 0.05, 0.02, 1.0))
        dir_light.modify()
    dir_light.set_actor_rotation(unreal.Rotator(0.0, -35.0, 45.0), True)

# DO NOT touch the editor viewport camera — the user is framing the shot themselves.
# Just invalidate so the next frame picks up the new sky params.
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.editor_invalidate_viewports()

# Unreal throttles ticks to ~0 when its window isn't focused, which causes
# the screenshot to never actually render. Disable Slate throttling so the
# editor keeps ticking even in the background.
ues_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(ues_world, 'Slate.bAllowThrottling 0')

import os as _os
if _os.path.exists(SCREENSHOT_PATH):
    try:
        _os.remove(SCREENSHOT_PATH)
    except Exception:
        pass

# ---------- FAST SCREENSHOT via SceneCapture2D -> RenderTarget ----------
# Match the editor viewport's POV exactly, capture synchronously, export PNG.
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cam_loc, cam_rot = ues.get_level_viewport_camera_info()
editor_world = ues.get_editor_world()

# In-memory transient render target — no asset on disk
rt = unreal.TextureRenderTarget2D()
rt.set_editor_property('size_x', 800)
rt.set_editor_property('size_y', 450)
rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)

# Spawn a transient SceneCapture2D actor at the viewport pose
capture_actor = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, cam_rot)
try:
    cap_comp = capture_actor.capture_component2d
    cap_comp.set_editor_property('texture_target', rt)
    # SCS_FINAL_COLOR_LDR runs through the full post-process pipeline (tonemap, exposure, etc.)
    cap_comp.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap_comp.set_editor_property('fov_angle', 90.0)
    cap_comp.set_editor_property('capture_every_frame', False)
    cap_comp.set_editor_property('capture_on_movement', False)
    # Show flags: keep atmosphere/fog/lighting on (defaults), nothing to disable for our case
    cap_comp.capture_scene()

    # Export the render target to the destination path (synchronous)
    unreal.RenderingLibrary.export_render_target(
        editor_world, rt, SCREENSHOT_DIR, 'iter.png'
    )
finally:
    eas.destroy_actor(capture_actor)

print(f'Sky tuned. Fast screenshot -> {SCREENSHOT_PATH}')
