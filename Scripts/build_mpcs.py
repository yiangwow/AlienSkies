"""Populate MPC_TimeOfDay and MPC_BlackHole with the parameters the C++ refers to.

The C++ SceneDirector reads/writes these names — they MUST match exactly:
- TimeOfDay: SunElevation, SunAzimuth, CameraFOV (scalar); SkyTintColor, TerrainTintColor (vector)
- BlackHole: BH_Mass, BH_LensRadius, BH_DiskIntensity, BH_DopplerAngle, BH_JetIntensity (scalar);
             BH_ScreenPosition (vector — only X,Y used)
"""
import unreal


def ensure_scalar(mpc, name, default):
    existing = list(mpc.get_editor_property('scalar_parameters'))
    for sp in existing:
        if str(sp.get_editor_property('parameter_name')) == name:
            return False
    sp = unreal.CollectionScalarParameter()
    sp.set_editor_property('parameter_name', name)
    sp.set_editor_property('default_value', float(default))
    existing.append(sp)
    mpc.set_editor_property('scalar_parameters', existing)
    return True


def ensure_vector(mpc, name, default_color):
    existing = list(mpc.get_editor_property('vector_parameters'))
    for vp in existing:
        if str(vp.get_editor_property('parameter_name')) == name:
            return False
    vp = unreal.CollectionVectorParameter()
    vp.set_editor_property('parameter_name', name)
    vp.set_editor_property('default_value', default_color)
    existing.append(vp)
    mpc.set_editor_property('vector_parameters', existing)
    return True


mpc_tod = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
mpc_bh = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')

added = []
if mpc_tod:
    if ensure_scalar(mpc_tod, 'SunElevation', 30.0): added.append('TOD.SunElevation')
    if ensure_scalar(mpc_tod, 'SunAzimuth',   45.0): added.append('TOD.SunAzimuth')
    if ensure_scalar(mpc_tod, 'CameraFOV',    90.0): added.append('TOD.CameraFOV')
    if ensure_scalar(mpc_tod, 'StarBrightness', 1.0): added.append('TOD.StarBrightness')
    if ensure_scalar(mpc_tod, 'StarRotation',   0.0): added.append('TOD.StarRotation')
    if ensure_vector(mpc_tod, 'SkyTintColor',     unreal.LinearColor(0.7, 0.3, 0.9, 1.0)): added.append('TOD.SkyTintColor')
    if ensure_vector(mpc_tod, 'TerrainTintColor', unreal.LinearColor(0.4, 0.25, 0.2, 1.0)): added.append('TOD.TerrainTintColor')
    unreal.EditorAssetLibrary.save_loaded_asset(mpc_tod)

if mpc_bh:
    if ensure_scalar(mpc_bh, 'BH_Mass',          1.0):   added.append('BH.Mass')
    if ensure_scalar(mpc_bh, 'BH_LensRadius',    0.15):  added.append('BH.LensRadius')
    if ensure_scalar(mpc_bh, 'BH_DiskIntensity', 10.0):  added.append('BH.DiskIntensity')
    if ensure_scalar(mpc_bh, 'BH_DopplerAngle',  0.0):   added.append('BH.DopplerAngle')
    if ensure_scalar(mpc_bh, 'BH_JetIntensity',  1.0):   added.append('BH.JetIntensity')
    if ensure_vector(mpc_bh, 'BH_ScreenPosition', unreal.LinearColor(0.5, 0.5, 0.0, 0.0)): added.append('BH.ScreenPosition')
    unreal.EditorAssetLibrary.save_loaded_asset(mpc_bh)

print(f'Added {len(added)} parameters:')
for a in added:
    print(f'  + {a}')
if not added:
    print('  (no changes — already populated)')
