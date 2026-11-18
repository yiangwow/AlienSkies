"""Remove null blendable from PPV, keep only M_PPLensing2. Apply 1280x720 windowed."""
import unreal

# --- 1. Fix PPV blendables ---
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mat = unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing2')

for a in eas.get_all_level_actors():
    if 'PostProcess' in a.get_class().get_name():
        settings = a.get_editor_property('settings')
        wb = unreal.WeightedBlendable()
        wb.set_editor_property('weight', 1.0)
        wb.set_editor_property('object', mat)
        blendables = unreal.WeightedBlendables()
        blendables.set_editor_property('array', [wb])   # only M_PPLensing2, nothing else
        settings.set_editor_property('weighted_blendables', blendables)
        a.set_editor_property('settings', settings)
        print(f'PPV {a.get_actor_label()} now has 1 blendable: M_PPLensing2')

les.save_current_level()

# --- 2. Apply resolution without editor restart ---
gs = unreal.GameUserSettings.get_game_user_settings()
gs.set_screen_resolution(unreal.IntPoint(1280, 720))
gs.set_fullscreen_mode(unreal.WindowMode.WINDOWED)
gs.apply_settings(False)
gs.save_settings()
print('Resolution set to 1280x720 Windowed and saved.')
