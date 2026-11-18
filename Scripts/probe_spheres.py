"""Find a smooth (high-poly) sphere mesh to replace the faceted low-poly core/ring."""
import unreal
candidates = [
    '/Engine/BasicShapes/Sphere',
    '/Engine/EngineMeshes/Sphere',
    '/Engine/EditorMeshes/EditorSphere',
    '/Engine/VREditor/BasicMeshes/SM_Sphere_01',
    '/Engine/ArtTools/RenderToTexture/Meshes/S_1_Unit_Sphere',
    '/Engine/EngineMeshes/SphereHighPoly',
]
for p in candidates:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        m = unreal.load_asset(p)
        try:
            tris = m.get_num_triangles(0)
            verts = m.get_num_vertices(0)
        except Exception as e:
            tris = verts = '?'
        print(f'  EXISTS  {p}  tris={tris} verts={verts}')
    else:
        print(f'  --      {p}')
print('Done.')
