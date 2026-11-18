import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    lvl = les.get_current_level()
    print('Level outer:', lvl.get_outer().get_name() if lvl else 'None')
except Exception as e:
    print('get_current_level error:', e)
actors = eas.get_all_level_actors()
print('Actor count:', len(actors))
if actors:
    for a in actors[:10]:
        print(' ', a.get_actor_label(), a.get_class().get_name())
