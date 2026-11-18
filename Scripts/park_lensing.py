"""Detach M_PPLensing2 from PPV_DeepSpace — parks the lensing without deleting the asset."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
les   = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

ppv = None
for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
    if a.get_actor_label() == 'PPV_DeepSpace':
        ppv = a; break

if ppv:
    settings = ppv.get_editor_property('settings')
    blendables = settings.get_editor_property('weighted_blendables')
    blendables.set_editor_property('array', [])
    settings.set_editor_property('weighted_blendables', blendables)
    ppv.set_editor_property('settings', settings)
    les.save_current_level()
    print('M_PPLensing2 detached from PPV_DeepSpace. Lensing parked.')
else:
    print('PPV_DeepSpace not found.')
