"""
ONE-SHOT scene rebuild for the cosmic-arena environment, and CRUCIALLY it SAVES
the level at the end so PIE loads a clean world from disk (not a dirty in-memory
duplicate, which is what crashed us on 2026-05-30).

Run after reopening the editor:
    python run.py --file rebuild_scene.py

Idempotent — safe to run repeatedly. Re-running clears old HeroStar_* actors first.
"""
import unreal
import math

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mel = unreal.MaterialEditingLibrary
world = ues.get_editor_world()


def by_class(cls):
    return [a for a in eas.get_all_level_actors() if a.get_class().get_name() == cls]


def by_label_prefix(prefix):
    return [a for a in eas.get_all_level_actors() if a.get_actor_label().startswith(prefix)]


# ---------- 1. Deep space atmosphere ----------
for sa in by_class('SkyAtmosphere'):
    c = sa.get_component_by_class(unreal.SkyAtmosphereComponent)
    if c:
        c.set_editor_property('rayleigh_scattering', unreal.LinearColor(0, 0, 0, 1))
        c.set_editor_property('rayleigh_scattering_scale', 0.0)
        c.set_editor_property('mie_scattering_scale', 0.0)
        c.set_editor_property('mie_absorption_scale', 0.0)
        c.set_editor_property('ground_albedo', unreal.Color(0, 0, 0, 255))
        sa.modify()

for dl in by_class('DirectionalLight'):
    c = dl.get_component_by_class(unreal.DirectionalLightComponent)
    if c:
        c.set_editor_property('use_temperature', False)
        c.set_light_color(unreal.LinearColor(1.0, 0.97, 0.92, 1.0))
        c.set_intensity(2.5)
        c.set_editor_property('atmosphere_sun_disk_color_scale', unreal.LinearColor(1, 1, 1, 1))
        dl.modify()
    dl.set_actor_rotation(unreal.Rotator(0.0, -20.0, 30.0), True)

for sl in by_class('SkyLight'):
    c = sl.get_component_by_class(unreal.SkyLightComponent)
    if c:
        c.set_editor_property('source_type', unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        c.set_editor_property('real_time_capture', False)  # no sky to capture (atmosphere deleted) -> kills the red warning
        c.set_intensity(0.05)
        sl.modify()

for f in by_class('ExponentialHeightFog'):
    c = f.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if c:
        c.set_editor_property('fog_density', 0.0)
        f.modify()

# ---------- 2. Star dome: uniform sphere, M_StarDome, HUGE radius ----------
# Must enclose ALL content (galaxies out to ~520k). The sphere is OPAQUE, so if it's
# smaller than the galaxies they get occluded (and from inside you'd only see nebula).
# BasicShapes/Sphere base radius = 50 -> scale 60000 = radius 3,000,000.
star_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarDome')
sphere_mesh_sky = unreal.load_asset('/Engine/BasicShapes/Sphere')
for ss in by_label_prefix('SM_SkySphere'):
    smc = ss.get_component_by_class(unreal.StaticMeshComponent)
    if smc and star_mat:
        smc.set_editor_property('static_mesh', sphere_mesh_sky)
        smc.set_material(0, star_mat)
        ss.set_actor_location(unreal.Vector(0, 0, 0), False, False)
        ss.set_actor_scale3d(unreal.Vector(60000, 60000, 60000))  # radius ~3,000,000
        ss.modify()

# ---------- 3. Push landscape out of view ----------
for ls in by_class('Landscape') + by_class('LandscapeStreamingProxy'):
    loc = ls.get_actor_location()
    if loc.z > -50000:
        ls.set_actor_location(unreal.Vector(loc.x, loc.y, -100000), False, False)

# ---------- 4. Hero stars ----------
for a in by_label_prefix('HeroStar_'):
    eas.destroy_actor(a)

sphere_mesh = unreal.load_asset('/Engine/BasicShapes/Sphere')
hero_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_HeroStar')

HEROES = [
    ( 30,   0, 300000,  8000, (1.0, 0.85, 0.6),  60),
    ( 45,  60, 350000, 12000, (0.5, 0.7,  1.0),  80),
    ( 25, 130, 280000,  7000, (1.0, 0.4,  0.2),  50),
    ( 55, 220, 400000, 15000, (0.9, 0.9,  1.0), 100),
    ( 20, 280, 300000,  6000, (1.0, 0.7,  0.9),  45),
    ( 35, 340, 320000,  9000, (0.6, 1.0,  0.7),  60),
    (-25,  30, 320000,  8000, (0.8, 0.5,  1.0),  55),
    (-40, 100, 380000, 11000, (1.0, 0.9,  0.7),  70),
    (-15, 170, 280000,  6500, (0.4, 0.9,  1.0),  50),
    (-50, 250, 420000, 14000, (1.0, 0.3,  0.5),  90),
    (-10, 300, 290000,  7500, (0.9, 1.0,  0.6),  55),
    (-30,  20, 310000,  9000, (0.7, 0.6,  1.0),  65),
]

for i, (lat_d, lon_d, dist, radius, rgb, intensity) in enumerate(HEROES):
    lat, lon = math.radians(lat_d), math.radians(lon_d)
    x = dist * math.cos(lat) * math.cos(lon)
    y = dist * math.cos(lat) * math.sin(lon)
    z = dist * math.sin(lat)
    actor = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0))
    actor.set_actor_label(f'HeroStar_{i:02d}')
    actor.set_editor_property('is_spatially_loaded', False)  # always loaded (far from origin)
    smc = actor.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_editor_property('static_mesh', sphere_mesh)
    # Keep MOVABLE — static actors spawned via Python can destabilize PIE world duplication.
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    actor.set_actor_scale3d(unreal.Vector(radius / 50.0, radius / 50.0, radius / 50.0))
    smc.set_editor_property('cast_shadow', False)
    mid = smc.create_dynamic_material_instance(0, hero_mat)
    mid.set_vector_parameter_value('Color', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    mid.set_scalar_parameter_value('Intensity', float(intensity))

les.editor_invalidate_viewports()

# ---------- 5. SAVE THE LEVEL (the lesson from the crash) ----------
saved = les.save_current_level()
print(f'Scene rebuilt. Hero stars: {len(HEROES)}. Level saved: {saved}')
