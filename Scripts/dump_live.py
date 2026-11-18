"""Read the live black-hole tuning straight from the saved level so we can reconcile the
spawn_*.py sources to ground truth. Prints actor scales + every disk material scalar/vector
param + DomeBrightness + jet hidden state. No mutation, no save."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

def find(lbl):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lbl:
            return a
    return None

print('==== LIVE BLACK HOLE STATE ====')

core = find('BlackHole_Core')
ring = find('BlackHole_PhotonRing')
disk = find('BlackHole_RMDisk')
sky  = find('SM_SkySphere')

if core:
    s = core.get_actor_scale3d()
    print(f'Core   scale={s.x:.4f}  -> radius={s.x*160.0:.1f}')
if ring:
    s = ring.get_actor_scale3d()
    print(f'Ring   scale={s.x:.4f}  -> radius={s.x*160.0:.1f}  (x{s.x*160.0/(core.get_actor_scale3d().x*160.0):.4f} of core)' if core else f'Ring scale={s.x:.4f}')

if disk:
    s = disk.get_actor_scale3d()
    print(f'Disk box scale={s.x:.2f}')
    rot = disk.get_actor_rotation()
    print(f'Disk rotation pitch={rot.pitch:.2f} yaw={rot.yaw:.2f} roll={rot.roll:.2f}')
    dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
    for p in ('InnerR','OuterR','Thickness','Spin','Brightness','BoundR','LensStrength','CaptureR'):
        try:
            print(f'  disk.{p} = {dm.get_scalar_parameter_value(p)}')
        except Exception as ex:
            print(f'  disk.{p} = <err {ex}>')
    for p in ('DiskN','DiskU','DiskV'):
        try:
            v = dm.get_vector_parameter_value(p)
            print(f'  disk.{p} = ({v.r:.4f}, {v.g:.4f}, {v.b:.4f})')
        except Exception as ex:
            print(f'  disk.{p} = <err {ex}>')

if sky:
    sm = sky.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
    try:
        print(f'DomeBrightness = {sm.get_scalar_parameter_value("DomeBrightness")}')
    except Exception as ex:
        print(f'DomeBrightness = <err {ex}>')

for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith('BlackHole_Jet'):
        print(f'{lbl}: hidden_ed={a.is_hidden_ed()} hidden={a.get_editor_property("hidden")}')

# corona
for a in eas.get_all_level_actors():
    if 'Corona' in a.get_actor_label() or 'Halo' in a.get_actor_label():
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if smc:
            try:
                print(f'{a.get_actor_label()} Brightness = {smc.get_material(0).get_scalar_parameter_value("Brightness")}')
            except Exception:
                pass
print('==== END ====')
