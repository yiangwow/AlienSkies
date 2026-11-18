"""Build a TRUE 3D volumetric galaxy: a ~50k-point star cloud in a real spiral
distribution (dense core bulge + logarithmic arms + thin disc), per-instance
color by radius, brightness variation. Real depth/parallax/any-angle/fly-through.

HISM via SubobjectDataSubsystem. Reusable make_galaxy(); places one hero galaxy.
"""
import unreal, math, random

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

plane = unreal.load_asset('/Engine/BasicShapes/Plane')   # 2-tri camera-facing sprite (cheap)
mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarPoint')


def add_hism(actor, name):
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    params = unreal.AddNewSubobjectParams(
        parent_handle=root,
        new_class=unreal.HierarchicalInstancedStaticMeshComponent,
        blueprint_context=None)
    h, fail = sds.add_new_subobject(params)
    sds.rename_subobject(h, unreal.Text(name))
    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(
        unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    return unreal.HierarchicalInstancedStaticMeshComponent.cast(obj)


def lerp3(a, b, t):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)


def galaxy_color(t, palette='cool'):
    if palette == 'fire':
        # M87-like: blazing white core -> orange -> deep red rim
        if t < 0.15:
            return (1.0, 0.97, 0.90)
        elif t < 0.45:
            return lerp3((1.0, 0.90, 0.65), (1.0, 0.52, 0.18), (t-0.15)/0.30)
        else:
            return lerp3((1.0, 0.52, 0.18), (0.85, 0.16, 0.06), (t-0.45)/0.55)
    # 'cool': blazing white core -> warm gold -> cool blue rim
    if t < 0.18:
        return (1.0, 0.97, 0.92)
    elif t < 0.5:
        return lerp3((1.0, 0.95, 0.82), (1.0, 0.72, 0.42), (t-0.18)/0.32)
    else:
        return lerp3((1.0, 0.72, 0.42), (0.62, 0.74, 1.0), (t-0.5)/0.5)


def _spiral_pos(rng, maxR, arms, winding, thickness):
    """A point on the disc following the log-spiral arms + thin disc."""
    u = rng.random()
    r = maxR * (u ** 1.3)
    arm = rng.randrange(arms)
    spread = rng.gauss(0, 0.26) * (0.4 + 0.8*(r/maxR))
    th = arm*(2*math.pi/arms) + (r/maxR)*winding + spread
    x = r*math.cos(th); y = r*math.sin(th)
    z = rng.gauss(0, 1.0) * thickness * (1.0 - 0.65*r/maxR)
    return x, y, z, r/maxR


def make_galaxy(label, center, maxR=95000.0, n_stars=110000, n_gas=9000, arms=2,
                winding=5.5, thickness=7000.0, tilt_rot=None, seed=1, palette='cool'):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            eas.destroy_actor(a)
    actor = eas.spawn_actor_from_class(unreal.Actor, center, tilt_rot or unreal.Rotator(0,0,0))
    actor.set_actor_label(label)
    actor.set_editor_property('is_spatially_loaded', False)
    hism = add_hism(actor, 'GalaxyHISM')
    hism.set_editor_property('static_mesh', plane)
    hism.set_material(0, mat)
    hism.set_editor_property('num_custom_data_floats', 3)
    hism.set_editor_property('cast_shadow', False)

    rng = random.Random(seed)
    transforms = []
    colors = []

    # --- GAS LAYER: large, dim, soft sprites -> diffuse glow filling between stars ---
    for i in range(n_gas):
        if rng.random() < 0.35:    # some gas concentrated in the core
            rr = abs(rng.gauss(0, 0.22)) * maxR
            th = rng.uniform(0, 2*math.pi)
            x = rr*math.cos(th); y = rr*math.sin(th)
            z = rng.gauss(0, 1.0) * thickness * 0.8
            t = min(rr/maxR, 1.0)
        else:
            x, y, z, t = _spiral_pos(rng, maxR, arms, winding, thickness*1.4)
        gs = (800.0 + rng.random()*2600.0) / 50.0        # smaller soft clouds (less foggy)
        transforms.append(unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0,0,0),
                                            unreal.Vector(gs, gs, gs)))
        c = galaxy_color(t, palette)
        b = rng.uniform(0.03, 0.10)                      # very dim diffuse glow
        colors.append((c[0]*b, c[1]*b, c[2]*b))

    # --- STAR LAYER: small bright points ---
    BULGE = int(n_stars * 0.42)                          # denser core
    for i in range(n_stars):
        if i < BULGE:
            rr = abs(rng.gauss(0, 0.12)) * maxR          # tighter, brighter bulge
            th = rng.uniform(0, 2*math.pi); ph = math.acos(rng.uniform(-1, 1))
            x = rr*math.sin(ph)*math.cos(th); y = rr*math.sin(ph)*math.sin(th)
            z = rr*math.cos(ph) * 0.7
            t = min(rr/maxR, 1.0); bright = rng.uniform(1.0, 3.5)
        else:
            x, y, z, t = _spiral_pos(rng, maxR, arms, winding, thickness)
            bright = rng.uniform(0.4, 1.6)
        s = (28.0 + rng.random()*85.0) / 50.0            # fine stars (slightly more luminous)
        transforms.append(unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0,0,0),
                                            unreal.Vector(s, s, s)))
        c = galaxy_color(t, palette)
        colors.append((c[0]*bright, c[1]*bright, c[2]*bright))

    hism.add_instances(transforms, False, False)
    last = len(colors) - 1
    for idx, c in enumerate(colors):
        hism.set_custom_data_value(idx, 0, c[0], False)
        hism.set_custom_data_value(idx, 1, c[1], False)
        hism.set_custom_data_value(idx, 2, c[2], idx == last)
    print(f'{label}: {hism.get_instance_count()} instances ({n_gas} gas + {n_stars} stars)')
    return actor


# Place one HERO volumetric galaxy in clean space, face-on-ish for a good look.
# Fiery orange/red palette (M87 vibe), denser gas for the fiery glow.
CENTER = unreal.Vector(0, 0, 900000)
make_galaxy('VolGalaxy_Hero', CENTER, maxR=95000.0, n_stars=160000, n_gas=12000,
            arms=2, winding=5.5, thickness=6000.0,
            tilt_rot=unreal.Rotator(0.0, 0.0, 0.0), seed=3, palette='fire')

# Frame it 3/4 from above
cam = unreal.Vector(CENTER.x + 90000, CENTER.y + 30000, CENTER.z + 240000)
d = unreal.Vector(CENTER.x-cam.x, CENTER.y-cam.y, CENTER.z-cam.z)
yaw = math.degrees(math.atan2(d.y, d.x)); pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x*d.x+d.y*d.y)))
ues.set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))
les.editor_invalidate_viewports()
les.save_current_level()
print('hero volumetric galaxy placed + framed + saved')
