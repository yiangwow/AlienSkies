import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

TARGET_RADIUS = 3000000.0  # 3M units — well beyond farthest galaxy (~520k)

for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'SM_SkySphere':
        a.set_actor_hidden_in_game(False)
        a.set_is_temporarily_hidden_in_editor(False)
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        mesh = smc.get_editor_property('static_mesh')
        # Unscaled mesh bounds radius
        b = mesh.get_bounds()
        # SphereRadius from box extent
        ext = b.box_extent
        base_r = max(ext.x, ext.y, ext.z)
        scale = TARGET_RADIUS / base_r
        a.set_actor_location(unreal.Vector(0, 0, 0), False, False)
        a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        print(f'mesh base radius={base_r:.1f}, set scale={scale:.1f} -> radius~{TARGET_RADIUS:.0f}')

les.editor_invalidate_viewports()
les.save_current_level()
print('saved')
