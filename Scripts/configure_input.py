"""
Configures IMC_AlienSkies with key bindings for IA_Look and IA_Zoom.

Run in Unreal Editor Python console:
    py "E:/projects/AlienSkies/Scripts/configure_input.py"

Or from Output Log (Cmd dropdown → Python), paste:
    exec(open('E:/projects/AlienSkies/Scripts/configure_input.py').read())
"""

import unreal

IMC_PATH = '/Game/AlienSkies/DataAssets/IMC_AlienSkies'
IA_LOOK_PATH = '/Game/AlienSkies/DataAssets/IA_Look'
IA_ZOOM_PATH = '/Game/AlienSkies/DataAssets/IA_Zoom'

imc = unreal.load_asset(IMC_PATH)
ia_look = unreal.load_asset(IA_LOOK_PATH)
ia_zoom = unreal.load_asset(IA_ZOOM_PATH)

if not imc or not ia_look or not ia_zoom:
    raise RuntimeError('One or more input assets not found. Check paths.')

ia_look.set_editor_property('value_type', unreal.InputActionValueType.AXIS2D)
ia_zoom.set_editor_property('value_type', unreal.InputActionValueType.AXIS1D)

def make_key(name):
    k = unreal.Key()
    # Try the standard property name, fall back to alternatives if needed
    for prop in ('key_name', 'name', 'KeyName'):
        try:
            k.set_editor_property(prop, name)
            print(f'  FKey property set via "{prop}"')
            return k
        except Exception as e:
            print(f'  property "{prop}" failed: {e}')
    # Diagnostic: dump all editor properties available
    print('  available properties:', [p for p in dir(k) if not p.startswith('_')])
    raise RuntimeError(f'Could not set key name for {name}')

look_key = make_key('Mouse2D')
zoom_key = make_key('MouseWheelAxis')

look_mapping = unreal.EnhancedActionKeyMapping()
look_mapping.set_editor_property('action', ia_look)
look_mapping.set_editor_property('key', look_key)

zoom_mapping = unreal.EnhancedActionKeyMapping()
zoom_mapping.set_editor_property('action', ia_zoom)
zoom_mapping.set_editor_property('key', zoom_key)

# UE 5.7: 'mappings' is deprecated, use 'default_key_mappings' (FEnhancedActionKeyMappingArray)
try:
    dkm = imc.get_editor_property('default_key_mappings')
    inner = dkm.get_editor_property('mappings')
    inner.append(look_mapping)
    inner.append(zoom_mapping)
    dkm.set_editor_property('mappings', inner)
    imc.set_editor_property('default_key_mappings', dkm)
    print('  Used default_key_mappings (UE 5.5+)')
except Exception as e:
    print(f'  default_key_mappings path failed ({e}), falling back to legacy mappings')
    mappings = imc.get_editor_property('mappings')
    mappings.append(look_mapping)
    mappings.append(zoom_mapping)
    imc.set_editor_property('mappings', mappings)

# Force the packages dirty so save_asset actually writes them
imc.modify()
ia_look.modify()
ia_zoom.modify()
unreal.EditorAssetLibrary.save_loaded_asset(ia_look)
unreal.EditorAssetLibrary.save_loaded_asset(ia_zoom)
unreal.EditorAssetLibrary.save_loaded_asset(imc)

print('IMC configured: IA_Look=Mouse2D (Axis2D), IA_Zoom=MouseWheelAxis (Axis1D)')
