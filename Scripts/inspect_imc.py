"""
Introspect IMC_AlienSkies and its bound input actions to verify the configuration.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/inspect_imc.py"
"""

import unreal

IMC_PATH = '/Game/AlienSkies/DataAssets/IMC_AlienSkies'
IA_LOOK_PATH = '/Game/AlienSkies/DataAssets/IA_Look'
IA_ZOOM_PATH = '/Game/AlienSkies/DataAssets/IA_Zoom'


def dump_props(obj, prefix=''):
    """Dump all editor properties of a UObject/struct."""
    if obj is None:
        print(f'{prefix}<None>')
        return
    try:
        # Try to enumerate via dir for properties
        for name in dir(obj):
            if name.startswith('_'):
                continue
            try:
                val = obj.get_editor_property(name)
                print(f'{prefix}{name} = {val!r}')
            except Exception:
                pass
    except Exception as e:
        print(f'{prefix}<dump error: {e}>')


print('=' * 70)
print('IA_Look introspection')
print('=' * 70)
ia_look = unreal.load_asset(IA_LOOK_PATH)
print(f'Asset: {ia_look}')
print(f'  value_type = {ia_look.get_editor_property("value_type")}')
print(f'  triggers = {ia_look.get_editor_property("triggers")}')
print(f'  modifiers = {ia_look.get_editor_property("modifiers")}')

print()
print('=' * 70)
print('IA_Zoom introspection')
print('=' * 70)
ia_zoom = unreal.load_asset(IA_ZOOM_PATH)
print(f'Asset: {ia_zoom}')
print(f'  value_type = {ia_zoom.get_editor_property("value_type")}')
print(f'  triggers = {ia_zoom.get_editor_property("triggers")}')
print(f'  modifiers = {ia_zoom.get_editor_property("modifiers")}')

print()
print('=' * 70)
print('IMC_AlienSkies introspection')
print('=' * 70)
imc = unreal.load_asset(IMC_PATH)
print(f'Asset: {imc}')

# Try the UE 5.5+ container
dkm = imc.get_editor_property('default_key_mappings')
print(f'default_key_mappings = {dkm!r}')
inner = dkm.get_editor_property('mappings') if dkm else None
print(f'  inner mappings array length = {len(inner) if inner is not None else "N/A"}')

if inner:
    for i, m in enumerate(inner):
        print(f'  --- Mapping #{i} ---')
        action = m.get_editor_property('action')
        key = m.get_editor_property('key')
        triggers = m.get_editor_property('triggers')
        modifiers = m.get_editor_property('modifiers')
        print(f'    action = {action}')
        print(f'    key = {key} (key_name={key.get_editor_property("key_name") if key else "N/A"})')
        print(f'    triggers = {triggers} (count={len(triggers) if triggers else 0})')
        print(f'    modifiers = {modifiers} (count={len(modifiers) if modifiers else 0})')

# Also check the deprecated 'mappings' property to see if it still has data
print()
try:
    legacy = imc.get_editor_property('mappings')
    print(f'legacy "mappings" array length = {len(legacy) if legacy is not None else "N/A"}')
except Exception as e:
    print(f'legacy mappings read failed: {e}')

print()
print('DONE')
