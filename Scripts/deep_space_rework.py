"""Convert the scene from 'meditative alien sky' to 'Gurren Lagann space battle':
- Atmosphere scattering crushed → true black space
- Procedural starfield brightened
- Hero stars spawned as discrete emissive actors (future grapple targets)
- Landscape pushed far below the camera so the player feels weightless
"""
import unreal
import math

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
mel = unreal.MaterialEditingLibrary
world = ues.get_editor_world()
all_actors = eas.get_all_level_actors()


def find_by_class(cls):
    return [a for a in all_actors if a.get_class().get_name() == cls]


# ---------- 1. Sky Atmosphere → near-zero scatter (deep space) ----------
for sa in find_by_class('SkyAtmosphere'):
    comp = sa.get_component_by_class(unreal.SkyAtmosphereComponent)
    if comp:
        # Crush Rayleigh — atmosphere becomes nearly invisible
        comp.set_editor_property('rayleigh_scattering', unreal.LinearColor(0.0, 0.0, 0.0, 1.0))
        comp.set_editor_property('rayleigh_scattering_scale', 0.0)
        # Kill Mie too
        comp.set_editor_property('mie_scattering_scale', 0.0)
        comp.set_editor_property('mie_absorption_scale', 0.0)
        # Ground albedo: black (player is in space, no ground bounce). Color is FColor (0-255 ints).
        comp.set_editor_property('ground_albedo', unreal.Color(0, 0, 0, 255))
        sa.modify()
        print(f'Atmosphere -> deep space (no scattering)')

# ---------- 2. Directional Light → distant white "sun" pinprick ----------
for dl in find_by_class('DirectionalLight'):
    comp = dl.get_component_by_class(unreal.DirectionalLightComponent)
    if comp:
        comp.set_editor_property('use_temperature', False)
        comp.set_light_color(unreal.LinearColor(1.0, 0.97, 0.92, 1.0))  # near-white
        comp.set_intensity(2.5)
        comp.set_editor_property('atmosphere_sun_disk_color_scale', unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        dl.modify()
    dl.set_actor_rotation(unreal.Rotator(0.0, -20.0, 30.0), True)
    print('DirectionalLight -> distant bright white')

# ---------- 3. SkyLight: pure black (no ambient bounce in space) ----------
for sl in find_by_class('SkyLight'):
    comp = sl.get_component_by_class(unreal.SkyLightComponent)
    if comp:
        comp.set_editor_property('source_type', unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        comp.set_intensity(0.05)
        sl.modify()
        print('SkyLight -> near-zero ambient')

# ---------- 4. Kill exponential fog ----------
for f in find_by_class('ExponentialHeightFog'):
    comp = f.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if comp:
        comp.set_editor_property('fog_density', 0.0)
        f.modify()
        print('Fog -> 0 density')

# ---------- 5. Push landscape far below camera ----------
landscapes = find_by_class('Landscape') + find_by_class('LandscapeStreamingProxy')
for ls in landscapes:
    loc = ls.get_actor_location()
    if loc.z > -50000:
        ls.set_actor_location(unreal.Vector(loc.x, loc.y, -100000), False, False)
print(f'Pushed {len(landscapes)} landscape actors below z=-100000')

# ---------- 6. Boost procedural star brightness via MPC default ----------
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
sps = list(mpc.get_editor_property('scalar_parameters'))
for sp in sps:
    if str(sp.get_editor_property('parameter_name')) == 'StarBrightness':
        sp.set_editor_property('default_value', 3.0)
mpc.set_editor_property('scalar_parameters', sps)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
print('StarBrightness default -> 3.0')

# ---------- 7. Spawn 'hero stars' as emissive sphere actors ----------
# These are placeholders for future grapple targets. Each is a small sphere mesh
# with a unique emissive color. We use the engine's Sphere mesh.
sphere_mesh = unreal.load_asset('/Engine/BasicShapes/Sphere')

# Build (or reuse) a simple emissive material we can instance per-star
HERO_MAT_PATH = '/Game/AlienSkies/Materials/M_HeroStar'
if not unreal.EditorAssetLibrary.does_asset_exist(HERO_MAT_PATH):
    factory = unreal.MaterialFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    hmat = asset_tools.create_asset('M_HeroStar', '/Game/AlienSkies/Materials',
                                    unreal.Material, factory)
    hmat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    hmat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)

    color_param = mel.create_material_expression(hmat, unreal.MaterialExpressionVectorParameter, -400, 0)
    color_param.set_editor_property('parameter_name', 'Color')
    color_param.set_editor_property('default_value', unreal.LinearColor(1.0, 0.6, 0.3, 1.0))

    intensity_param = mel.create_material_expression(hmat, unreal.MaterialExpressionScalarParameter, -400, 150)
    intensity_param.set_editor_property('parameter_name', 'Intensity')
    intensity_param.set_editor_property('default_value', 80.0)

    mul = mel.create_material_expression(hmat, unreal.MaterialExpressionMultiply, -150, 75)
    mel.connect_material_expressions(color_param, '', mul, 'A')
    mel.connect_material_expressions(intensity_param, '', mul, 'B')

    mel.connect_material_property(mul, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(hmat)
    unreal.EditorAssetLibrary.save_loaded_asset(hmat)
    print('Created M_HeroStar')

hero_mat = unreal.load_asset(HERO_MAT_PATH)

# Hero star definitions: position (deg lat, deg lon), distance, scale, color, intensity
# Distances in cm (UE units). Stars are FAR but big to maintain angular size.
HEROES = [
    # (lat_deg, lon_deg, dist, radius, color_rgb, intensity)
    # Upper hemisphere — six varied targets
    (  30,    0,  300000,   8000, (1.0, 0.85, 0.6),   60),   # warm yellow
    (  45,   60,  350000,  12000, (0.5, 0.7,  1.0),   80),   # blue giant
    (  25,  130,  280000,   7000, (1.0, 0.4,  0.2),   50),   # red giant
    (  55,  220,  400000,  15000, (0.9, 0.9,  1.0),  100),   # white-blue, big
    (  20,  280,  300000,   6000, (1.0, 0.7,  0.9),   45),   # pink dwarf
    (  35,  340,  320000,   9000, (0.6, 1.0,  0.7),   60),   # green-cyan
    # Lower hemisphere — six more so look-down isn't empty
    ( -25,   30,  320000,   8000, (0.8, 0.5,  1.0),   55),   # purple
    ( -40,  100,  380000,  11000, (1.0, 0.9,  0.7),   70),   # cream
    ( -15,  170,  280000,   6500, (0.4, 0.9,  1.0),   50),   # cyan
    ( -50,  250,  420000,  14000, (1.0, 0.3,  0.5),   90),   # magenta
    ( -10,  300,  290000,   7500, (0.9, 1.0,  0.6),   55),   # lime
    ( -30,   20,  310000,   9000, (0.7, 0.6,  1.0),   65),   # lilac
]

# Clear any existing hero stars first (re-run safety)
for a in list(all_actors):
    if a.get_actor_label().startswith('HeroStar_'):
        eas.destroy_actor(a)

spawned = 0
for i, (lat_d, lon_d, dist, radius, rgb, intensity) in enumerate(HEROES):
    lat = math.radians(lat_d)
    lon = math.radians(lon_d)
    x = dist * math.cos(lat) * math.cos(lon)
    y = dist * math.cos(lat) * math.sin(lon)
    z = dist * math.sin(lat)

    actor = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                       unreal.Vector(x, y, z),
                                       unreal.Rotator(0, 0, 0))
    actor.set_actor_label(f'HeroStar_{i:02d}')
    smc = actor.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_editor_property('static_mesh', sphere_mesh)
    smc.set_mobility(unreal.ComponentMobility.STATIC)
    # Mesh is 100cm diameter; scale to desired radius
    scale = radius / 50.0
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))

    # Create a dynamic material instance with our color
    mid = smc.create_dynamic_material_instance(0, hero_mat)
    mid.set_vector_parameter_value('Color', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    mid.set_scalar_parameter_value('Intensity', float(intensity))

    # Disable shadow casting (stars don't cast shadows on themselves)
    smc.set_editor_property('cast_shadow', False)
    spawned += 1

print(f'Spawned {spawned} hero stars')

# Refresh viewports so the change is visible
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.editor_invalidate_viewports()

print('DONE — deep space rework complete')
