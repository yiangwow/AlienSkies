"""Swap core + photon ring from the faceted /Engine/BasicShapes/Sphere (960 tris) to
/Engine/EditorMeshes/EditorSphere (3968 tris) to kill the visible polygonal silhouette.
Preserve world radii: core=32000, photon ring=33920. Save level."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
smooth = unreal.load_asset('/Engine/EditorMeshes/EditorSphere')
# base radius of the smooth mesh at scale 1
b = smooth.get_bounds().box_extent
base_r = max(b.x, b.y, b.z)
print(f'EditorSphere base radius (scale 1) = {base_r}')
targets = {'BlackHole_Core': 32000.0, 'BlackHole_PhotonRing': 32000.0*1.06}
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl in targets:
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_editor_property('static_mesh', smooth)
        s = targets[lbl] / base_r
        a.set_actor_scale3d(unreal.Vector(s, s, s))
        print(f'  {lbl}: mesh->EditorSphere, world_radius={targets[lbl]:.0f}, scale={s:.2f}')
les.save_current_level()
print('Saved.')
