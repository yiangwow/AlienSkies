"""Restore a clean/safe scene state after the PP-lensing tooling investigation:
- detach M_PPLensing from PPV_DeepSpace (so it can't distort the editor viewport)
- reset BH_LensStrength default to 0
- unhide disk / jets / photon ring / lensing sphere
- delete the M_PPRedTest probe material
- save level
"""
import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mat=unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')

# detach from PPV
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='PPV_DeepSpace':
        s=a.get_editor_property('settings')
        wbs=s.get_editor_property('weighted_blendables')
        keep=[b for b in list(wbs.get_editor_property('array')) if b.get_editor_property('object')!=mat]
        nb=unreal.WeightedBlendables(); nb.set_editor_property('array',keep)
        s.set_editor_property('weighted_blendables',nb); a.set_editor_property('settings',s)
        print('detached M_PPLensing from PPV (remaining blendables:',len(keep),')')

# reset BH_LensStrength default to 0
mpc=unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')
sc=list(mpc.get_editor_property('scalar_parameters'))
for sp in sc:
    if str(sp.get_editor_property('parameter_name'))=='BH_LensStrength':
        sp.set_editor_property('default_value',0.0)
mpc.set_editor_property('scalar_parameters',sc); unreal.EditorAssetLibrary.save_loaded_asset(mpc)

# unhide all BH components
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l.startswith('BlackHole'):
        a.set_is_temporarily_hidden_in_editor(False)

# delete probe material
if unreal.EditorAssetLibrary.does_asset_exist('/Game/AlienSkies/Materials/M_PPRedTest'):
    unreal.EditorAssetLibrary.delete_asset('/Game/AlienSkies/Materials/M_PPRedTest')

les.save_current_level()
print('cleanup done')
