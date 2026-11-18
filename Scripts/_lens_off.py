import unreal
mel=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')
mel.delete_all_material_expressions(mat)
mat.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
st=mel.create_material_expression(mat,unreal.MaterialExpressionSceneTexture,-600,0)
st.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
mel.connect_material_property(st,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat); unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('lens OFF (passthrough)')
