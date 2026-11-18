"""Scratch: import the sanity 1m cube to a temp path, report its bounds, then delete it.
A 1m cube has half-extent 0.5m. If imported at correct cm scale -> extent ~50cm. If extent
~0.5 -> glTF metres were treated as cm (need UNIFORM_SCALE=100 in import_mech.py)."""
import unreal
GLB = r'E:/projects/AlienSkies/tools/blender/out/sanity_cube.glb'
DEST = '/Game/AlienSkies/_ScaleTest'
at = unreal.AssetToolsHelpers.get_asset_tools()
task = unreal.AssetImportTask()
task.set_editor_property('filename', GLB)
task.set_editor_property('destination_path', DEST)
task.set_editor_property('automated', True)
task.set_editor_property('save', False)
task.set_editor_property('replace_existing', True)
at.import_asset_tasks([task])
imported = list(task.get_editor_property('imported_object_paths'))
if not imported:
    imported = list(unreal.EditorAssetLibrary.list_assets(DEST, recursive=True))
print('IMPORTED:', imported)
for p in imported:
    a = unreal.load_asset(p)
    if isinstance(a, unreal.StaticMesh):
        b = a.get_bounds().box_extent
        print(f'EXTENT_CM {b.x:.3f},{b.y:.3f},{b.z:.3f}')
if unreal.EditorAssetLibrary.does_directory_exist(DEST):
    unreal.EditorAssetLibrary.delete_directory(DEST)
print('SCALE_TEST_DONE')
