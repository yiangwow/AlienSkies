"""Diagnose M_StarDome and SM_SkySphere: material assignment, blend/shading, key params,
mesh scale, and whether the dome is actually covering the camera region."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

MAT = '/Game/AlienSkies/Materials/M_StarDome'
print('=== M_StarDome material ===')
if unreal.EditorAssetLibrary.does_asset_exist(MAT):
    m = unreal.load_asset(MAT)
    print('  exists=True')
    print('  shading_model =', m.get_editor_property('shading_model'))
    print('  blend_mode    =', m.get_editor_property('blend_mode'))
    print('  two_sided     =', m.get_editor_property('two_sided'))
    try: print('  is_sky        =', m.get_editor_property('is_sky'))
    except Exception: pass
else:
    print('  exists=False  <-- material missing!')

print('=== SkySphere / dome actors ===')
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    low = lbl.lower()
    if 'sky' in low or 'dome' in low or 'star' in low:
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        s = a.get_actor_scale3d()
        loc = a.get_actor_location()
        meshname = '?'
        matname = '?'
        if smc:
            mesh = smc.get_editor_property('static_mesh')
            meshname = mesh.get_name() if mesh else 'None'
            mat0 = smc.get_material(0)
            matname = mat0.get_name() if mat0 else 'None'
        print(f'  {lbl}: mesh={meshname} mat={matname} scale=({s.x:.0f},{s.y:.0f},{s.z:.0f}) loc=({loc.x:.0f},{loc.y:.0f},{loc.z:.0f}) hidden={a.is_hidden_ed()}')
print('Done.')
