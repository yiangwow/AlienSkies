import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

sphere = unreal.load_asset('/Engine/BasicShapes/Sphere')   # uniform UV sphere, radius 50
star_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarDome')
TARGET_RADIUS = 3000000.0

for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'SM_SkySphere':
        a.set_actor_hidden_in_game(False)
        a.set_is_temporarily_hidden_in_editor(False)
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_editor_property('static_mesh', sphere)
        smc.set_material(0, star_mat)
        b = sphere.get_bounds()
        base_r = max(b.box_extent.x, b.box_extent.y, b.box_extent.z)
        scale = TARGET_RADIUS / base_r
        a.set_actor_location(unreal.Vector(0,0,0), False, False)
        a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        print(f'Swapped to BasicShapes/Sphere, base_r={base_r}, scale={scale:.1f}')

les.editor_invalidate_viewports()
les.save_current_level()
print('saved')
