"""Assert the mech parts imported to the flat paths, and report the muzzle socket (a WARN, not
a FAIL, since it's a forward-compat hook). Run via run.py."""
import unreal
need = ['Mech_LeftClaw', 'Mech_RightWeapon', 'Mech_Struts']
ok = True
for n in need:
    p = f'/Game/AlienSkies/Mech/{n}'
    exists = unreal.EditorAssetLibrary.does_asset_exist(p)
    print(('PASS' if exists else 'FAIL'), 'asset', p)
    ok = ok and exists
wpn = unreal.load_asset('/Game/AlienSkies/Mech/Mech_RightWeapon')
muzzle = wpn.find_socket('Muzzle') if wpn else None
print(('PASS' if muzzle else 'WARN'), 'muzzle socket')
print('OVERALL', 'PASS' if ok else 'FAIL')
