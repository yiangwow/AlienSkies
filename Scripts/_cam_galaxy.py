"""Frame a close-ish shot of Galaxy_Hero."""
import unreal, math
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
TARGET = unreal.Vector(-230000, 0, 130000)
cam = unreal.Vector(TARGET.x + 120000, TARGET.y + 80000, TARGET.z + 40000)
d = unreal.Vector(TARGET.x-cam.x, TARGET.y-cam.y, TARGET.z-cam.z)
yaw = math.degrees(math.atan2(d.y, d.x))
pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x**2+d.y**2)))
ues.set_level_viewport_camera_info(cam, unreal.Rotator(0, pitch, yaw))
les.editor_invalidate_viewports()
print('Framed on Galaxy_Hero')
