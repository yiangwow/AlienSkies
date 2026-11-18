import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
from collections import Counter
c = Counter()
labels = []
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    c[cls] += 1
    lbl = a.get_actor_label()
    if not lbl.startswith('HLOD') and 'WorldPartition' not in cls:
        labels.append(f'{cls}:{lbl}')
print('--- counts ---')
for k,v in sorted(c.items()):
    print(f'{v:4d}  {k}')
print('--- non-HLOD actors ---')
for l in sorted(labels):
    print(l)
