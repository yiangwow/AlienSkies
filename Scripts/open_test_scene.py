"""Open L_TestScene and report what's in it."""
import unreal

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/AlienSkies/Levels/L_TestScene')

import time; time.sleep(3)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
print(f'Level loaded. {len(actors)} actors total.')
ppvs = [a for a in actors if 'PostProcess' in a.get_class().get_name()]
print('PPVs:', [(a.get_actor_label(), a.get_class().get_name()) for a in ppvs])
bh = [a for a in actors if 'BlackHole' in a.get_actor_label() or 'blackhole' in a.get_actor_label().lower()]
print('BH actors:', [a.get_actor_label() for a in bh])
