"""Headless Blender sanity check: make a 1m cube and export it to glb. Proves bpy + glTF
export work from the command line. Run:
  blender --background --python tools/blender/sanity_check.py
"""
import bpy, os

# Clean default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1 metre cube at origin
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, 'sanity_cube.glb')
# export_yup=False keeps Z-up so the UE import bridge handles handedness explicitly.
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=False)
print('SANITY_EXPORT_OK', out, os.path.exists(out))
