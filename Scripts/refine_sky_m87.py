"""
Refine the M87 preset: kill the white sun, dim/disable Earth-like clouds,
push the purple deeper and the horizon glow warmer.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/refine_sky_m87.py"
"""

import unreal


def find_first_of_class(level_actors, cls):
    for a in level_actors:
        if a.get_class().get_name() == cls:
            return a
    return None


eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()

sky_atm = find_first_of_class(actors, 'SkyAtmosphere')
dir_light = find_first_of_class(actors, 'DirectionalLight')
clouds = find_first_of_class(actors, 'VolumetricCloud')


# -------------------- Directional Light: make the sun small, red, dim --------------------
if dir_light:
    comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
    if comp:
        # Turn OFF temperature so our raw color is used directly
        comp.set_editor_property('use_temperature', False)
        comp.set_light_color(unreal.LinearColor(1.0, 0.25, 0.1, 1.0))  # deep red-orange
        comp.set_intensity(1.5)  # very dim — red dwarfs are weak

        # Disk: small + warm red. Default disk is bright white, this is what made it look like Earth's sun.
        comp.set_editor_property('atmosphere_sun_disk_color_scale', unreal.LinearColor(0.8, 0.15, 0.05, 1.0))

        # Bigger/visible sun disc via the cosmetic disc params if available
        try:
            comp.set_editor_property('forward_shading_priority', 1)
        except Exception:
            pass

        dir_light.modify()
        print('Sun: deep red-orange, dim (red dwarf)')


# -------------------- Volumetric Clouds: disable them for now --------------------
# Earth-cumulus clouds compete with the sky drama. We'll re-add stylized alien clouds later.
if clouds:
    eas.destroy_actor(clouds)
    print('Volumetric clouds removed (too Earth-like for M87)')


# -------------------- Sky Atmosphere: deeper purple, more horizon glow --------------------
if sky_atm:
    comp = sky_atm.get_component_by_class(unreal.SkyAtmosphereComponent)
    if comp:
        # Deep saturated violet zenith — push purple HARD, kill the red channel
        comp.set_editor_property('rayleigh_scattering', unreal.LinearColor(0.18, 0.04, 0.85, 1.0))
        comp.set_editor_property('rayleigh_scattering_scale', 0.08)  # higher = thicker atmosphere

        # Mie: tame it. Default UE Mie scale is 0.003; we want a SUBTLE warm horizon, not orange flood.
        comp.set_editor_property('mie_scattering_scale', 0.002)
        comp.set_editor_property('mie_anisotropy', 0.85)
        comp.set_editor_property('mie_scattering', unreal.LinearColor(1.0, 0.5, 0.2, 1.0))

        sky_atm.modify()
        print('Atmosphere: deeper purple + stronger orange horizon')


print('DONE — Ctrl+S to save the level')
