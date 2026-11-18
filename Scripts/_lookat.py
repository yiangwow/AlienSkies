import unreal, math
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tgt = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'Galaxy_Hero':
        tgt = a; break
if not tgt:
    print('Galaxy_Hero not found!'); 
else:
    tp = tgt.get_actor_location()
    print(f'Galaxy_Hero at {tp.x},{tp.y},{tp.z}')
    print(f'  scale {tgt.get_actor_scale3d().x}')
    smc = tgt.get_component_by_class(unreal.StaticMeshComponent)
    mesh = smc.get_editor_property('static_mesh')
    print(f'  mesh {mesh.get_path_name() if mesh else None}')
    print(f'  material0 {smc.get_material(0).get_name() if smc.get_material(0) else None}')
    print(f'  visible {tgt.get_editor_property("hidden") if False else smc.is_visible()}')
    # camera 60000 units away along +X from the galaxy, looking at it
    cam = unreal.Vector(tp.x + 60000, tp.y, tp.z)
    d = unreal.Vector(tp.x-cam.x, tp.y-cam.y, tp.z-cam.z)
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x*d.x+d.y*d.y)))
    ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))
    les.editor_invalidate_viewports()
    print(f'  cam at {cam.x},{cam.y},{cam.z} yaw{yaw:.0f} pitch{pitch:.0f}')
