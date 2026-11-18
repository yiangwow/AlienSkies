"""Set DomeBrightness to a dark Interstellar value and save."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sky = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'SM_SkySphere': sky = a
smc = sky.get_component_by_class(unreal.StaticMeshComponent)
mid = smc.get_material(0)
mid.set_scalar_parameter_value('DomeBrightness', 0.09)
les.save_current_level()
print('DomeBrightness=0.09, saved.')
