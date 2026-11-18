"""Smoke test: can we build a persistent HISM galaxy point-cloud via Python?
Spawns an actor, adds a HISM, sets mesh+material+custom-data, adds a few thousand
instances in a quick spiral. If this renders, the full generator will work.
"""
import unreal, math, random

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

sphere = unreal.load_asset('/Engine/BasicShapes/Sphere')
mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarPoint')

for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'VolGalaxy_TEST':
        eas.destroy_actor(a)

CENTER = unreal.Vector(0, 0, 400000)
actor = eas.spawn_actor_from_class(unreal.Actor, CENTER, unreal.Rotator(0, 0, 0))
actor.set_actor_label('VolGalaxy_TEST')
actor.set_editor_property('is_spatially_loaded', False)

# Add a HISM via SubobjectDataSubsystem (canonical editor-scripting path, persists).
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles = sds.k2_gather_subobject_data_for_instance(actor)
root_handle = handles[0]
params = unreal.AddNewSubobjectParams(
    parent_handle=root_handle,
    new_class=unreal.HierarchicalInstancedStaticMeshComponent,
    blueprint_context=None)
sub_handle, fail = sds.add_new_subobject(params)
if not fail.is_empty():
    print(f'add_new_subobject FAILED: {fail}')
sds.rename_subobject(sub_handle, unreal.Text('GalaxyHISM'))
data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(sub_handle)
obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
hism = unreal.HierarchicalInstancedStaticMeshComponent.cast(obj)
print(f'HISM added: {hism}')
hism.set_editor_property('static_mesh', sphere)
hism.set_material(0, mat)
hism.set_editor_property('num_custom_data_floats', 3)
# cheap: no collision, no shadows
hism.set_editor_property('cast_shadow', False)

N = 4000
maxR = 90000.0
arms = 2
random.seed(7)
added = 0
for i in range(N):
    u = random.random()
    r = maxR * (u ** 1.4)                      # denser toward center
    arm = i % arms
    theta = arm * (2*math.pi/arms) + r/maxR * 6.0 + random.gauss(0, 0.35)
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    z = random.gauss(0, 1.0) * 6000.0 * (1.0 - 0.6*r/maxR)
    s = (50.0 + random.random()*120.0) / 50.0   # sphere base r=50 -> world size ~50-170
    xf = unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0,0,0), unreal.Vector(s,s,s))
    idx = hism.add_instance(xf, False)
    # color by radius: hot white-blue core -> warm mid -> cool outer
    t = r / maxR
    if t < 0.3:
        col = (1.0, 0.93, 0.85)
    elif t < 0.65:
        col = (1.0, 0.72, 0.45)
    else:
        col = (0.7, 0.78, 1.0)
    hism.set_custom_data_value(idx, 0, col[0], False)
    hism.set_custom_data_value(idx, 1, col[1], False)
    hism.set_custom_data_value(idx, 2, col[2], True)
    added += 1

print(f'Added {added} instances. Instance count = {hism.get_instance_count()}')

# Frame it
cam = unreal.Vector(CENTER.x + 260000, CENTER.y, CENTER.z + 60000)
d = unreal.Vector(CENTER.x-cam.x, CENTER.y-cam.y, CENTER.z-cam.z)
yaw = math.degrees(math.atan2(d.y, d.x)); pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))
les.editor_invalidate_viewports()
print('framed test galaxy')
