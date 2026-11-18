"""Spawn spiral-galaxy disc actors using M_SpiralGalaxy on flat plane meshes.
Frames the editor camera on the hero galaxy, saves the level, screenshots.
"""
import unreal, math, os

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

plane = unreal.load_asset('/Engine/BasicShapes/Plane')
gal_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_SpiralGalaxy')

# Clear old galaxies
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('Galaxy_'):
        eas.destroy_actor(a)

CAM_POS = unreal.Vector(0, 0, 10000)
CAM_ROT = unreal.Rotator(0.0, 1.0, 180.0)

# Each entry: (label, pos, tilt_deg, tilt_axis_deg, scale, arms, tightness, brightness, coreRGB, armRGB, elliptical_mix)
# Vivid saturated colors — no more pastel cream. Each galaxy should read as a distinct
# colored object: blazing orange, deep blue, vivid green, crimson, purple, etc.
GALAXIES = [
    # Hero cluster — player's first impression on spawn
    ('Galaxy_Hero', unreal.Vector(-230000,   0, 130000), 28, 20,  2200, 2.0, 5.0, 3.5, (1.0,0.85,0.6), (1.0,0.45,0.08), 0.0),   # fire orange
    ('Galaxy_Blue', unreal.Vector(-250000,150000,175000), 40,120, 1800, 3.0, 6.5, 3.0, (0.3,0.6,1.0),  (0.1,0.4,1.0),   0.0),   # deep blue
    ('Galaxy_Red',  unreal.Vector(-220000,-145000,95000), 35,250, 1600, 4.0, 4.0, 3.0, (1.0,0.3,0.1),  (0.9,0.1,0.05),  0.0),   # vivid crimson
    ('Galaxy_Far',  unreal.Vector(-330000, 55000,200000), 55, 60, 1300, 2.0, 7.0, 2.5, (0.6,0.2,1.0),  (0.5,0.1,0.9),   0.0),   # vivid purple
]

# Vivid palette — each slot is (coreRGB, armRGB, arm_count, elliptical_mix)
# Mix of spirals, ellipticals, and irregular shapes for variety.
PALETTE = [
    ((1.0,0.50,0.10), (1.0,0.30,0.05), 2, 0.0),   # blazing orange spiral
    ((0.15,0.45,1.0), (0.05,0.25,1.0), 2, 0.0),   # deep blue spiral
    ((0.10,0.90,0.40), (0.05,0.75,0.30), 3, 0.0), # vivid green spiral
    ((0.80,0.10,0.70), (0.65,0.05,0.60), 2, 0.0), # vivid magenta spiral
    ((1.0,0.20,0.15), (0.85,0.08,0.05), 4, 0.0),  # crimson 4-arm
    ((0.85,0.75,0.20), (0.80,0.60,0.05), 2, 0.0), # gold/amber spiral
    ((1.0,0.90,0.95), (0.8,0.5,1.0),    0, 1.0),  # elliptical — soft white-pink orb
    ((0.05,0.70,0.80), (0.02,0.55,0.70), 3, 0.0), # teal/cyan spiral
    ((1.0,0.55,0.80), (0.9,0.3,0.65),   2, 0.0),  # hot pink spiral
    ((0.60,0.90,1.0), (0.4,0.75,1.0),   0, 1.0),  # elliptical — cool blue orb
    ((0.95,0.80,0.30), (0.85,0.55,0.05),5, 0.0),  # amber 5-arm
    ((0.30,1.0,0.55), (0.15,0.85,0.35), 2, 0.0),  # vivid lime-green
]
N_SCATTER = 12
_ga = math.pi * (3.0 - math.sqrt(5.0))
for i in range(N_SCATTER):
    t = (i + 0.5) / N_SCATTER
    zc = 1.0 - 2.0 * t
    rxy = math.sqrt(max(0.0, 1.0 - zc * zc))
    th = _ga * i
    dist = 200000 + (i * 37139) % 380000
    pos = unreal.Vector(math.cos(th)*rxy*dist, math.sin(th)*rxy*dist, zc*dist)
    scale = 1400 + (i * 71) % 1600           # bigger: 1400..3000
    core, armc, arms, emix = PALETTE[i % len(PALETTE)]
    tight = 4.0 + float(i % 5)
    bright = 2.8 + float(i % 3) * 0.4        # 2.8..3.6
    tilt = 18 + (i * 23) % 52
    tilt_axis = (i * 47) % 360
    GALAXIES.append((f'Galaxy_F{i:02d}', pos, tilt, tilt_axis, scale, float(arms), tight, bright, core, armc, emix))

N_FAR = 18
for i in range(N_FAR):
    t = (i + 0.5) / N_FAR
    zc = 1.0 - 2.0 * t
    rxy = math.sqrt(max(0.0, 1.0 - zc * zc))
    th = _ga * i + 1.7
    dist = 700000 + (i * 53129) % 700000
    pos = unreal.Vector(math.cos(th)*rxy*dist, math.sin(th)*rxy*dist, zc*dist)
    scale = 700 + (i * 41) % 1100
    core, armc, arms, emix = PALETTE[(i + 2) % len(PALETTE)]
    tight = 4.0 + float(i % 5)
    bright = 2.0 + float(i % 2) * 0.5
    tilt = 15 + (i * 31) % 60
    tilt_axis = (i * 67) % 360
    GALAXIES.append((f'Galaxy_D{i:02d}', pos, tilt, tilt_axis, scale, float(arms), tight, bright, core, armc, emix))

# Near — big, close, rush past when flying. Deliberately bold colors.
NEAR = [
    ('Galaxy_N0', unreal.Vector( 160000, 190000,  40000), 30, 40,  3000, 2.0, 5.0, 3.5, (1.0,0.55,0.10),(1.0,0.35,0.02), 0.0),  # orange giant
    ('Galaxy_N1', unreal.Vector(  90000,-210000, 110000), 45,200,  2600, 3.0, 6.0, 3.2, (0.2,0.5,1.0),  (0.05,0.3,1.0),  0.0),  # blue giant
    ('Galaxy_N2', unreal.Vector(-150000, -60000,-160000), 38,300,  2800, 0.0, 4.5, 3.0, (1.0,0.85,1.0), (0.8,0.4,1.0),   1.0),  # big purple elliptical
]
GALAXIES.extend(NEAR)

ml = unreal.MathLibrary


def _norm(v):
    L = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2) or 1.0
    return (v[0]/L, v[1]/L, v[2]/L)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


for gi, (label, pos, tilt_deg, tilt_axis_deg, scale, arms, tight, bright, core, armc, emix) in enumerate(GALAXIES):
    # Direction from galaxy back to camera
    to_cam = _norm((CAM_POS.x - pos.x, CAM_POS.y - pos.y, CAM_POS.z - pos.z))
    # Perp axis (world-up cross to_cam)
    perp = _cross(to_cam, (0, 0, 1))
    if math.sqrt(perp[0]**2 + perp[1]**2 + perp[2]**2) < 0.01:
        perp = (0, 1, 0)
    perp = _norm(perp)
    # Rotate perp around to_cam to pick tip direction, then tip the normal off-axis
    tilt_axis = ml.rotate_angle_axis(unreal.Vector(*perp), float(tilt_axis_deg), unreal.Vector(*to_cam))
    normal = ml.rotate_angle_axis(unreal.Vector(*to_cam), float(tilt_deg), tilt_axis)
    rot = ml.make_rot_from_z(normal)

    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, pos, rot)
    a.set_actor_label(label)
    # Non-spatially-loaded so World Partition ALWAYS keeps it loaded (these are far
    # from origin and would otherwise be streamed out on restart -> disappear).
    a.set_editor_property('is_spatially_loaded', False)
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_editor_property('static_mesh', plane)
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_editor_property('cast_shadow', False)
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    mid = smc.create_dynamic_material_instance(0, gal_mat)
    mid.set_scalar_parameter_value('ArmCount', arms)
    mid.set_scalar_parameter_value('SpinTightness', tight)
    mid.set_scalar_parameter_value('Brightness', bright)
    mid.set_vector_parameter_value('CoreColor', unreal.LinearColor(core[0], core[1], core[2], 1.0))
    mid.set_vector_parameter_value('ArmColor', unreal.LinearColor(armc[0], armc[1], armc[2], 1.0))
    mid.set_scalar_parameter_value('EllipticalMix', emix)
    spin = (0.015 + 0.025 * (gi % 3)) * (1.0 if gi % 2 == 0 else -1.0)
    mid.set_scalar_parameter_value('RotationSpeed', spin)

# Set the camera to the survey pose (Claude owns it)
ues.set_level_viewport_camera_info(CAM_POS, CAM_ROT)
les.editor_invalidate_viewports()
saved = les.save_current_level()
print(f'Spawned {len(GALAXIES)} galaxies. Camera framed on hero. Saved: {saved}')
