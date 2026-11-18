"""Attach M_PPLensing2 to the post-process volume."""
import unreal
mat = unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing2')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

ppv = None
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    lbl = a.get_actor_label()
    if 'PostProcess' in cls or 'PPV' in lbl or 'PostProcess' in lbl:
        print(f'Found PPV candidate: {lbl} ({cls})')
        ppv = a

if ppv and mat:
    settings = ppv.get_editor_property('settings')
    wb = unreal.WeightedBlendable()
    wb.set_editor_property('weight', 1.0)
    wb.set_editor_property('object', mat)
    blendables = unreal.WeightedBlendables()
    existing = list(settings.get_editor_property('weighted_blendables').get_editor_property('array'))
    # remove any old lensing material entries
    keep = [b for b in existing if 'Lensing' not in str(b.get_editor_property('object'))]
    blendables.set_editor_property('array', keep + [wb])
    settings.set_editor_property('weighted_blendables', blendables)
    ppv.set_editor_property('settings', settings)
    les.save_current_level()
    print(f'Attached M_PPLensing2 to {ppv.get_actor_label()}')
elif not mat:
    print('ERROR: M_PPLensing2 not loaded')
elif not ppv:
    print('ERROR: No PostProcessVolume found in level')
