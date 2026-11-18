import unreal
props = [p for p in dir(unreal.SceneCaptureComponent2D) if not p.startswith('_')]
print("PP-related:", [p for p in props if 'post' in p.lower() or 'show' in p.lower() or 'blend' in p.lower()])
# check SceneTextureId members for the PPI0 name we used
print("SceneTextureId has PPI_POST_PROCESS_INPUT0:", 'PPI_POST_PROCESS_INPUT0' in dir(unreal.SceneTextureId))
print("SceneTextureId members:", [m for m in dir(unreal.SceneTextureId) if m.startswith('PPI')])
# verify the material compiled without errors
mat = unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')
print("domain:", mat.get_editor_property('material_domain'))
print("blendable_location:", mat.get_editor_property('blendable_location'))
