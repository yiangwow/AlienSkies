"""
Configure the level's SkyAtmosphere + DirectionalLight + SkyLight + Fog for the
M87 preset: purple/violet zenith, orange horizon glow, dim red-dwarf sun.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/setup_sky_m87.py"
"""

import unreal


def find_first_of_class(level_actors, cls):
    for a in level_actors:
        if a.get_class().get_name() == cls:
            return a
    return None


eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_actors = eas.get_all_level_actors()

sky_atm = find_first_of_class(level_actors, 'SkyAtmosphere')
dir_light = find_first_of_class(level_actors, 'DirectionalLight')
sky_light = find_first_of_class(level_actors, 'SkyLight')
height_fog = find_first_of_class(level_actors, 'ExponentialHeightFog')

print(f'SkyAtmosphere: {sky_atm}')
print(f'DirectionalLight: {dir_light}')
print(f'SkyLight: {sky_light}')
print(f'ExponentialHeightFog: {height_fog}')


# -------------------- Sky Atmosphere --------------------
# Default Earth-blue Rayleigh is a warm spectrum: re-tint to violet/magenta and shift Mie warm.
if sky_atm:
    comp = sky_atm.get_component_by_class(unreal.SkyAtmosphereComponent)
    if comp:
        # Rayleigh: tint towards purple — use a color that absorbs less of red/blue, more of green
        comp.set_editor_property('rayleigh_scattering', unreal.LinearColor(0.25, 0.06, 0.55, 1.0))  # violet
        comp.set_editor_property('rayleigh_scattering_scale', 0.04)

        # Mie: warm orange forward-scatter (the horizon glow)
        comp.set_editor_property('mie_scattering_scale', 0.006)
        comp.set_editor_property('mie_anisotropy', 0.95)
        comp.set_editor_property('mie_absorption_scale', 0.0)
        comp.set_editor_property('mie_scattering', unreal.LinearColor(1.0, 0.5, 0.2, 1.0))  # orange

        # Ground albedo: dark reddish-brown (alien rock)
        comp.set_editor_property('ground_albedo', unreal.LinearColor(0.15, 0.08, 0.04, 1.0))

        sky_atm.modify()
        print('SkyAtmosphere tuned for M87 violet sky')


# -------------------- Directional Light (Red dwarf) --------------------
if dir_light:
    comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
    if comp:
        # Red-dwarf colour: deep warm red, moderate intensity
        comp.set_light_color(unreal.LinearColor(1.0, 0.45, 0.25, 1.0))
        comp.set_intensity(3.5)  # lower than default 10
        comp.set_editor_property('use_temperature', True)
        comp.set_editor_property('temperature', 3200.0)  # red dwarf color temp

        # Atmospheric sun disk size & disk colour come through here too
        comp.set_editor_property('atmosphere_sun_light', True)
        comp.set_editor_property('atmosphere_sun_disk_color_scale', unreal.LinearColor(1.0, 0.3, 0.15, 1.0))

        dir_light.modify()

    # Aim the sun low (sunset-ish): pitch about -10°, yaw 45°
    dir_light.set_actor_rotation(unreal.Rotator(0.0, -10.0, 45.0), True)
    print('DirectionalLight tuned: red dwarf, low angle')


# -------------------- Sky Light --------------------
if sky_light:
    comp = sky_light.get_component_by_class(unreal.SkyLightComponent)
    if comp:
        comp.set_editor_property('source_type', unreal.SkyLightSourceType.SLS_CAPTURED_SCENE)
        comp.set_editor_property('real_time_capture', True)
        comp.set_editor_property('intensity_scale', 1.2)
        sky_light.modify()
        print('SkyLight set to real-time capture')


# -------------------- Height Fog --------------------
if height_fog:
    comp = height_fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if comp:
        # Reddish-purple horizon mist
        comp.set_editor_property('fog_inscattering_color', unreal.LinearColor(0.35, 0.1, 0.45, 1.0))
        comp.set_editor_property('fog_density', 0.025)
        comp.set_editor_property('fog_height_falloff', 0.2)
        height_fog.modify()
        print('Height fog tinted purple')


print('DONE — save the level to persist (Ctrl+S in editor)')
