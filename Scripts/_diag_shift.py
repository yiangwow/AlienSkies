"""Node-based remap test: TexCoord + (0.2,0) -> SceneTexture(PPI0).UV input -> Color.
If the image shifts, the SceneTexture UV-input path works (use it for the lens)."""
import unreal
mel=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')
mel.delete_all_material_expressions(mat)
mat.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-1000,0)
off=mel.create_material_expression(mat,unreal.MaterialExpressionConstant2Vector,-1000,150)
off.set_editor_property('r',0.2); off.set_editor_property('g',0.0)
add=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,-750,50)
mel.connect_material_expressions(uv,'',add,'A')
mel.connect_material_expressions(off,'',add,'B')
stx=mel.create_material_expression(mat,unreal.MaterialExpressionSceneTexture,-500,0)
stx.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
mel.connect_material_expressions(add,'',stx,'UV')
mel.connect_material_expressions(stx,'Color',unreal.MaterialExpressionMakeMaterialAttributes if False else stx,'')  # noop guard
# connect SceneTexture Color output -> Emissive
mel.connect_material_property(stx,'Color',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat); unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('node-based shift test built')
