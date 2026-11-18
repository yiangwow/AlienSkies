import unreal
print("WeightedBlendable props:", [p for p in dir(unreal.WeightedBlendable) if not p.startswith('__')][:20])
print("WeightedBlendables props:", [p for p in dir(unreal.WeightedBlendables) if not p.startswith('__')][:20])
s = unreal.PostProcessSettings()
print("has weighted_blendables:", 'weighted_blendables' in dir(s))
# find the PPV
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='PPV_DeepSpace':
        print("Found PPV_DeepSpace:", a.get_name())
