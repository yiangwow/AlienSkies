"""Remove ALL blendables from PPV_DeepSpace to test if PP material causes black bars."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for a in eas.get_all_level_actors():
    if 'PostProcess' in a.get_class().get_name():
        settings = a.get_editor_property('settings')
        blendables = unreal.WeightedBlendables()
        blendables.set_editor_property('array', [])
        settings.set_editor_property('weighted_blendables', blendables)
        a.set_editor_property('settings', settings)
        print(f'Cleared all blendables from {a.get_actor_label()}')
les.save_current_level()
