"""Remove BlackHole_Shadow sphere from the level."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
removed = []
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_Shadow':
        eas.destroy_actor(a)
        removed.append('BlackHole_Shadow')
les.save_current_level()
print('Removed:', removed or 'nothing found')
