"""The GIANT galaxy you fight inside — viewed nearly edge-on as a luminous band
on the horizon (Reference/ttgl-cosmic-battlefield.png).

Key fix vs v1: the disc is positioned FAR ahead so it never contains the camera,
and oriented to face the camera then tilted ~76 deg (near edge-on) so it reads as
a thin bright lens/band rather than a floor.
"""
import unreal, math

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml = unreal.MathLibrary

plane = unreal.load_asset('/Engine/BasicShapes/Plane')
gal_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_SpiralGalaxy')

for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'Galaxy_HomeDisc':
        eas.destroy_actor(a)

CAM = unreal.Vector(0, 0, 10000)              # survey camera pose
CENTER = unreal.Vector(-520000, 0, -30000)    # far in -X (player's spawn direction) + low
SCALE = 4200                                  # radius ~210k, all ahead of camera
TILT = 76.0                                   # near edge-on


def _norm(v):
    L = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2) or 1.0
    return (v[0]/L, v[1]/L, v[2]/L)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

to_cam = _norm((CAM.x-CENTER.x, CAM.y-CENTER.y, CAM.z-CENTER.z))
# Tilt about a horizontal axis (cross of to_cam and world up) so the band stays level
axis = _norm(_cross(to_cam, (0, 0, 1)))
normal = ml.rotate_angle_axis(unreal.Vector(*to_cam), TILT, unreal.Vector(*axis))
rot = ml.make_rot_from_z(normal)

a = eas.spawn_actor_from_class(unreal.StaticMeshActor, CENTER, rot)
a.set_actor_label('Galaxy_HomeDisc')
a.set_editor_property('is_spatially_loaded', False)  # always loaded (far from origin)
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_editor_property('static_mesh', plane)
smc.set_mobility(unreal.ComponentMobility.MOVABLE)
smc.set_editor_property('cast_shadow', False)
a.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))

mid = smc.create_dynamic_material_instance(0, gal_mat)
mid.set_scalar_parameter_value('ArmCount', 2.0)
mid.set_scalar_parameter_value('SpinTightness', 7.0)
mid.set_scalar_parameter_value('Brightness', 7.0)
mid.set_vector_parameter_value('CoreColor', unreal.LinearColor(1.0, 0.92, 0.75, 1.0))
mid.set_vector_parameter_value('ArmColor', unreal.LinearColor(1.0, 0.62, 0.32, 1.0))

les.editor_invalidate_viewports()
saved = les.save_current_level()
print(f'Home disc: center {CENTER.x},{CENTER.y},{CENTER.z} scale {SCALE} tilt {TILT}. Saved: {saved}')
