"""Test: hardcoded strength=1, center=(0.5,0.5), R=0.22, sampling PPI0 (the pattern
that renders scene fine in capture). If the background now BENDS around the core, the
shader works in SceneCapture and the earlier failure was MPC value propagation."""
import unreal
mel=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')
mel.delete_all_material_expressions(mat)
mat.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-1100,240)
st_node=mel.create_material_expression(mat,unreal.MaterialExpressionSceneTexture,-1100,360)
st_node.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
lens=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-650,0)
lens.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
lens.set_editor_property('code',"""
float2 C=float2(0.5,0.5);
float aspect=View.ViewSizeAndInvSize.x*View.ViewSizeAndInvSize.w;
float2 d=UV-C; d.x*=aspect;
float r=length(d);
float2 dir=(r>1e-5)?d/r:float2(0,1);
float R=0.22;
float bend=(R*R)/max(r,1e-4);
float rb=r-bend;
float2 sd=dir*rb; sd.x/=aspect;
float2 uvL=C+sd;
float3 col=SceneTextureLookup(clamp(uvL,0.0,1.0),14,false).rgb;
float sh=smoothstep(0.11,0.135,r);
col*=sh;
return col;
""")
ui=unreal.CustomInput(); ui.set_editor_property('input_name',unreal.Name('UV'))
bi=unreal.CustomInput(); bi.set_editor_property('input_name',unreal.Name('Bind'))
lens.set_editor_property('inputs',[ui,bi])
mel.connect_material_expressions(uv,'',lens,'UV')
mel.connect_material_expressions(st_node,'',lens,'Bind')
mel.connect_material_property(lens,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat); unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('hardcoded strength=1 lens rebuilt')
