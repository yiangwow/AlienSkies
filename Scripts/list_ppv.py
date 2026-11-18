import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if 'PostProcess' in a.get_class().get_name():
        settings = a.get_editor_property('settings')
        blendables = settings.get_editor_property('weighted_blendables').get_editor_property('array')
        print(f'PPV: {a.get_actor_label()} — {len(blendables)} blendable(s)')
        for b in blendables:
            print(f'  weight={b.get_editor_property("weight")} obj={b.get_editor_property("object")}')
