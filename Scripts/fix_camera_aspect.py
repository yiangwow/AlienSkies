"""Force bConstrainAspectRatio=false on the placed AlienCamera instance."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
fixed = []
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    if 'AlienCamera' in cls or 'AlienCamera' in a.get_actor_label():
        for comp in a.get_components_by_class(unreal.CameraComponent):
            comp.set_editor_property('constrain_aspect_ratio', False)
            fixed.append(a.get_actor_label())
            print(f'Set constrain_aspect_ratio=False on {a.get_actor_label()} CameraComponent')
les.save_current_level()
print('Done:', fixed or 'no AlienCamera found')
