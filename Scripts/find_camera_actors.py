import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    comps = a.get_components_by_class(unreal.CameraComponent)
    if comps:
        print(f'{a.get_actor_label()} ({a.get_class().get_name()}):')
        for c in comps:
            print(f'  CameraComponent constrain_aspect_ratio={c.get_editor_property("constrain_aspect_ratio")} aspect={c.get_editor_property("aspect_ratio")}')
