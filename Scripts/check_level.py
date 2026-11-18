import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('Current level:', les.get_current_level().get_outer().get_name())
ppvs = [a for a in eas.get_all_level_actors() if 'PostProcess' in a.get_class().get_name()]
print('PPVs found:', [(a.get_actor_label(), a.get_class().get_name()) for a in ppvs])
