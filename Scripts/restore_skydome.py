"""Restore SM_SkySphere (the star dome) that was accidentally deleted."""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# Check it's not already there
existing = [a for a in eas.get_all_level_actors() if a.get_actor_label() == 'SM_SkySphere']
if existing:
    print('SM_SkySphere already exists — nothing to do.')
else:
    sphere_mesh = unreal.load_asset('/Engine/BasicShapes/Sphere')
    star_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarDome')
    if not sphere_mesh:
        print('ERROR: could not load /Engine/BasicShapes/Sphere')
    elif not star_mat:
        print('ERROR: could not load M_StarDome')
    else:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        loc = unreal.Vector(0, 0, 0)
        rot = unreal.Rotator(0, 0, 0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
        actor.set_actor_label('SM_SkySphere')
        smc = actor.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_static_mesh(sphere_mesh)
        smc.set_material(0, star_mat)
        actor.set_actor_scale3d(unreal.Vector(60000, 60000, 60000))
        smc.set_mobility(unreal.ComponentMobility.MOVABLE)
        actor.set_editor_property('is_spatially_loaded', False)
        les.save_current_level()
        print('SM_SkySphere restored. Level saved.')
