"""
Rebuild IMC_AlienSkies using the reliable Mouse X+Y + Swizzle pattern instead of Mouse2D.

Mouse2D composite often doesn't fire on its own in UE5 — the standard template pattern
is to bind MouseX and MouseY separately to the Axis2D action, with a Swizzle modifier
on Y so it fills the Y component instead of X.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/fix_imc.py"
"""

import unreal

IMC_PATH = '/Game/AlienSkies/DataAssets/IMC_AlienSkies'
IA_LOOK_PATH = '/Game/AlienSkies/DataAssets/IA_Look'
IA_ZOOM_PATH = '/Game/AlienSkies/DataAssets/IA_Zoom'

imc = unreal.load_asset(IMC_PATH)
ia_look = unreal.load_asset(IA_LOOK_PATH)
ia_zoom = unreal.load_asset(IA_ZOOM_PATH)


def make_key(name):
    k = unreal.Key()
    k.set_editor_property('key_name', name)
    return k


def make_mapping(action, key_name, modifiers=None):
    m = unreal.EnhancedActionKeyMapping()
    m.set_editor_property('action', action)
    m.set_editor_property('key', make_key(key_name))
    if modifiers:
        m.set_editor_property('modifiers', modifiers)
    return m


# Build fresh mapping list
new_mappings = []

# IA_Look (Axis2D): MouseX fills X, MouseY fills Y via Swizzle
mouse_x_mapping = make_mapping(ia_look, 'MouseX')

# Swizzle modifier: YXZ swaps X into Y for the MouseY mapping
swizzle = unreal.InputModifierSwizzleAxis()
swizzle.set_editor_property('order', unreal.InputAxisSwizzle.YXZ)
mouse_y_mapping = make_mapping(ia_look, 'MouseY', modifiers=[swizzle])

new_mappings.append(mouse_x_mapping)
new_mappings.append(mouse_y_mapping)

# IA_Zoom (Axis1D): MouseWheelAxis directly
new_mappings.append(make_mapping(ia_zoom, 'MouseWheelAxis'))

# Replace the inner mappings array (clears the 4 duplicates as a bonus)
dkm = imc.get_editor_property('default_key_mappings')
dkm.set_editor_property('mappings', new_mappings)
imc.set_editor_property('default_key_mappings', dkm)

# Mark dirty + save
imc.modify()
unreal.EditorAssetLibrary.save_loaded_asset(imc)

print('IMC rebuilt with 3 mappings:')
print('  IA_Look <- MouseX (fills X)')
print('  IA_Look <- MouseY + Swizzle YXZ (fills Y)')
print('  IA_Zoom <- MouseWheelAxis')
