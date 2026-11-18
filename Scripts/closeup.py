"""Frame the camera close to Galaxy_Hero and screenshot, to inspect detail."""
import unreal, os

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

hero = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'Galaxy_Hero':
        hero = a
        break

if hero:
    hp = hero.get_actor_location()
    # Camera sits between origin-side and the galaxy, close enough to fill frame
    cam = unreal.Vector(hp.x * 0.45, hp.y * 0.45, hp.z * 0.45 + 5000)
    to = unreal.Vector(hp.x - cam.x, hp.y - cam.y, hp.z - cam.z)
    import math
    yaw = math.degrees(math.atan2(to.y, to.x))
    pitch = math.degrees(math.atan2(to.z, math.sqrt(to.x**2 + to.y**2)))
    ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))
    les.editor_invalidate_viewports()
    print(f'Framed close on Galaxy_Hero at {hp}')
else:
    print('Galaxy_Hero not found')
