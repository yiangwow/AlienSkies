"""Import the mech .glb into /Game/AlienSkies/Mech/ as static meshes, then FLATTEN the assets
to /Game/AlienSkies/Mech/<MeshName> (Interchange otherwise nests them under
<glbname>/StaticMeshes/). Reports final paths + bounds (cm) for scale/orientation verification.

VERIFIED 2026-06-06: UE auto-converts glTF metres -> cm (1m cube imports at 50cm half-extent),
so UNIFORM_SCALE is not needed. NOTE: run.py does not forward CLI args, so GLB is a constant.
"""
import unreal

GLB = r'E:/projects/AlienSkies/tools/blender/out/mech.glb'
DEST = '/Game/AlienSkies/Mech'
UNIFORM_SCALE = None  # m->cm is automatic; leave None

at = unreal.AssetToolsHelpers.get_asset_tools()
task = unreal.AssetImportTask()
task.set_editor_property('filename', GLB)
task.set_editor_property('destination_path', DEST)
task.set_editor_property('automated', True)
task.set_editor_property('save', True)
task.set_editor_property('replace_existing', True)
if UNIFORM_SCALE is not None:
    pipe = unreal.InterchangeGenericAssetsPipeline()
    pipe.set_editor_property('import_uniform_scale', float(UNIFORM_SCALE))
    task.set_editor_property('options', pipe)

at.import_asset_tasks([task])

imported = list(task.get_editor_property('imported_object_paths'))
if not imported:
    imported = list(unreal.EditorAssetLibrary.list_assets(DEST, recursive=True))
print('IMPORTED (raw):', imported)

EAL = unreal.EditorAssetLibrary
# Flatten static meshes to DEST/<name>
final = []
for p in imported:
    a = unreal.load_asset(p)
    if isinstance(a, unreal.StaticMesh):
        pkg = p.split('.')[0]               # object path -> package path
        target = f'{DEST}/{a.get_name()}'
        if pkg != target:
            if EAL.does_asset_exist(target):
                EAL.delete_asset(target)
            EAL.rename_asset(pkg, target)
        final.append(target)
# Remove the leftover nested folder (named after the glb file, e.g. 'mech')
import os
sub = f'{DEST}/{os.path.splitext(os.path.basename(GLB))[0]}'
if EAL.does_directory_exist(sub):
    EAL.delete_directory(sub)
EAL.save_directory(DEST, only_if_is_dirty=False, recursive=True)

print('FLATTENED:')
for p in final:
    a = unreal.load_asset(p)
    b = a.get_bounds().box_extent
    print(f'  mesh {p}  extent(cm)={b.x:.2f},{b.y:.2f},{b.z:.2f}')

# Muzzle socket on the weapon's forward (+Y) tip - firing origin for future combat (best-effort).
wpn = unreal.load_asset(f'{DEST}/Mech_RightWeapon')
if wpn:
    try:
        if wpn.find_socket('Muzzle') is None:
            bnd = wpn.get_bounds()
            o, e = bnd.origin, bnd.box_extent
            sock = unreal.StaticMeshSocket()
            sock.set_editor_property('socket_name', 'Muzzle')
            # Blender +Y (drill tip) maps to UE -Y, so the tip is at the -Y extreme.
            sock.set_editor_property('relative_location', unreal.Vector(o.x, o.y - e.y, o.z))
            wpn.add_socket(sock)
            EAL.save_asset(f'{DEST}/Mech_RightWeapon')
            print(f'MUZZLE socket @ ({o.x:.0f},{o.y - e.y:.0f},{o.z:.0f})')
        else:
            print('MUZZLE socket already present')
    except Exception as ex:
        print('MUZZLE socket skipped:', ex)
print('IMPORT_DONE')
