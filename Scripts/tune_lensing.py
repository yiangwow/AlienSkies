"""Tune lensing params on the placed SceneDirector actor."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if 'SceneDirector' in a.get_class().get_name() or 'BP_SceneDirector' in a.get_actor_label():
        a.set_editor_property('einstein_mult', 1.0)
        a.set_editor_property('shadow_mult', 1.0)
        print(f'Set EinsteinMult=1.0 ShadowMult=1.0 on {a.get_actor_label()}')
        break
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
