"""EDITOR-PREVIEW driver for the post-process gravitational lensing.

Projects the black hole's world center to the CURRENT editor viewport camera's screen
UV, computes the apparent radius, and (re)builds M_PPLensing with those values BAKED AS
LITERAL CONSTANTS — because there is no Python API to set MPC *instance* values, and
MPC asset-default changes don't propagate to the live SceneCapture instance.

The runtime/canonical version (build_pp_lensing.py) reads the same lens.hlsl but sources
the params from MPC_BlackHole (driven per-frame by SceneDirector). Same math, different
source. Run this AFTER framing the camera, then screenshot.py.

Matches screenshot.py's SceneCapture: fov_angle=90 (horizontal) at 1280x720.
"""
import unreal
import math

C = unreal.Vector(-620000.0, 0.0, 230000.0)   # black hole world center
HOLE_R = 13000.0
HFOV_DEG = 90.0
ASPECT = 1280.0 / 720.0
EINSTEIN_MULT = 2.1     # Einstein ring radius
SHADOW_MULT = 1.1       # match the clean black core

MAT = '/Game/AlienSkies/Materials/M_PPLensing'
HLSL_PATH = 'E:/projects/AlienSkies/Scripts/lens.hlsl'

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
loc, rot = ues.get_level_viewport_camera_info()
fwd, right, up = rot.get_forward_vector(), rot.get_right_vector(), rot.get_up_vector()

w = unreal.Vector(C.x - loc.x, C.y - loc.y, C.z - loc.z)
depth = w.x * fwd.x + w.y * fwd.y + w.z * fwd.z
x_cam = w.x * right.x + w.y * right.y + w.z * right.z
y_cam = w.x * up.x + w.y * up.y + w.z * up.z
tan_h = math.tan(math.radians(HFOV_DEG) * 0.5)
tan_v = tan_h / ASPECT

if depth <= 1.0:
    uv_x, uv_y, R, shadowR, strength = 0.5, 0.5, 0.1, 0.06, 0.0
    print('BH behind camera -> strength 0')
else:
    uv_x = 0.5 + 0.5 * (x_cam / depth) / tan_h
    uv_y = 0.5 - 0.5 * (y_cam / depth) / tan_v
    apparent = 0.5 * (HOLE_R / depth) / tan_v
    R = apparent * EINSTEIN_MULT
    shadowR = apparent * SHADOW_MULT
    strength = 1.0
    print(f'uv=({uv_x:.3f},{uv_y:.3f}) depth={depth:.0f} apparent={apparent:.4f} R={R:.4f}')

# ---- (re)build M_PPLensing with baked literal Constants ----
mel = unreal.MaterialEditingLibrary
mat = unreal.load_asset(MAT)
mel.delete_all_material_expressions(mat)
mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location', unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)

with open(HLSL_PATH, 'r') as f:
    body = f.read()
# Bake the params as literal declarations prepended to the body (Custom-node param
# inputs read as 0 here, so we don't feed them as inputs — only UV + Bind).
literals = (f"float Cx={uv_x:.6f}; float Cy={uv_y:.6f}; float R={R:.6f}; "
            f"float ShadowR={shadowR:.6f}; float Strength={strength:.6f};\n")
code = literals + body

uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 240)
st_node = mel.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -1100, 360)
st_node.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
lens = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -650, 0)
lens.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
lens.set_editor_property('code', code)
inputs = []
for nm in ['UV', 'Bind']:
    ci = unreal.CustomInput()
    ci.set_editor_property('input_name', unreal.Name(nm))
    inputs.append(ci)
lens.set_editor_property('inputs', inputs)
mel.connect_material_expressions(uv, '', lens, 'UV')
mel.connect_material_expressions(st_node, '', lens, 'Bind')
mel.connect_material_property(lens, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('M_PPLensing rebuilt with baked literals (preview)')
