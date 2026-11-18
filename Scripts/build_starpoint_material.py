"""M_StarPoint — camera-facing billboard sprite for galaxy star points.
- 2-triangle Plane mesh, but WPO rotates each quad to face the camera (cheap sprite).
- Additive, unlit, two-sided. Soft radial dot (no hard square).
- Emissive = per-instance custom data RGB (slots 0,1,2) * Brightness * radial falloff.
One HISM of these = ONE draw call, ~2 tris per star (vs 760 for a sphere).
"""
import unreal

PATH = '/Game/AlienSkies/Materials'
NAME = 'M_StarPoint'
FULL = f'{PATH}/{NAME}'
if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    unreal.EditorAssetLibrary.delete_asset(FULL)

factory = unreal.MaterialFactoryNew()
at = unreal.AssetToolsHelpers.get_asset_tools()
mat = at.create_asset(NAME, PATH, unreal.Material, factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)
mel = unreal.MaterialEditingLibrary

uv      = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 500)
objpos  = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1100, 600)
vtxpos  = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1100, 700)
campos  = mel.create_material_expression(mat, unreal.MaterialExpressionCameraPositionWS, -1100, 800)

# ---- Camera-facing billboard WPO ----
bb = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -750, 650)
bb.set_editor_property('description', 'BillboardWPO')
bb.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
bb.set_editor_property('code', """
float2 d = UV - 0.5;
float dl = length(d);
float2 dir = (dl > 0.0001) ? d / dl : float2(0,0);
float radius = length(VtxPos - ObjPos);          // scaled corner distance (keeps per-instance size)
float3 camFwd = normalize(CamPos - ObjPos);
float3 up0 = abs(camFwd.z) > 0.95 ? float3(1,0,0) : float3(0,0,1);
float3 camRight = normalize(cross(up0, camFwd));
float3 camUp = cross(camFwd, camRight);
float3 newWorld = ObjPos + (dir.x * camRight + dir.y * camUp) * radius;
return newWorld - VtxPos;
""")
for nm in ('UV','ObjPos','VtxPos','CamPos'):
    ci = unreal.CustomInput(); ci.set_editor_property('input_name', nm)
    bb.set_editor_property('inputs', list(bb.get_editor_property('inputs')) + [ci])
mel.connect_material_expressions(uv, '', bb, 'UV')
mel.connect_material_expressions(objpos, '', bb, 'ObjPos')
mel.connect_material_expressions(vtxpos, '', bb, 'VtxPos')
mel.connect_material_expressions(campos, '', bb, 'CamPos')
mel.connect_material_property(bb, '', unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)

# ---- Soft radial dot mask from UV ----
rad = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -750, 950)
rad.set_editor_property('description', 'RadialDot')
rad.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
rad.set_editor_property('code', "float2 d = UV - 0.5; return saturate(exp(-dot(d,d) * 42.0) - 0.015);")
rci = unreal.CustomInput(); rci.set_editor_property('input_name', 'UV')
rad.set_editor_property('inputs', [rci])
mel.connect_material_expressions(uv, '', rad, 'UV')

# ---- Per-instance color (RGB) ----
def picd(idx, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceCustomData, -750, y)
    n.set_editor_property('data_index', idx); return n
cd_r, cd_g, cd_b = picd(0, -100), picd(1, 0), picd(2, 100)
app1 = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -500, -50)
mel.connect_material_expressions(cd_r, '', app1, 'A'); mel.connect_material_expressions(cd_g, '', app1, 'B')
app2 = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -350, 0)
mel.connect_material_expressions(app1, '', app2, 'A'); mel.connect_material_expressions(cd_b, '', app2, 'B')

bright = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -500, 150)
bright.set_editor_property('parameter_name', 'Brightness'); bright.set_editor_property('default_value', 9.0)

# emissive = color * brightness * radialDot
m1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 0)
mel.connect_material_expressions(app2, '', m1, 'A'); mel.connect_material_expressions(bright, '', m1, 'B')
m2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -60, 60)
mel.connect_material_expressions(m1, '', m2, 'A'); mel.connect_material_expressions(rad, '', m2, 'B')
mel.connect_material_property(m2, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL} (camera-facing additive sprite)')
