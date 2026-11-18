import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='SM_SkySphere':
        smc=a.get_component_by_class(unreal.StaticMeshComponent)
        m=smc.get_editor_property('static_mesh')
        mat=smc.get_material(0)
        print(f'SkySphere mesh={m.get_name() if m else None} scale={a.get_actor_scale3d().x} mat={mat.get_name() if mat else None} hidden={a.is_temporarily_hidden_in_editor()}')
