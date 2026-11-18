"""Activate PP lensing + tune disk for M87/Gargantua look.

Steps:
  1. Update MPC_BlackHole: BH_LensStrength=1.0, screen position/radius from
     current viewport camera.
  2. Rebuild M_PPLensing2 in-place with improved code:
       - Shadow mask (dark event horizon)
       - OOB guard (passthrough instead of clamped-edge smear)
       - Far-field fade (smooth return to pristine space beyond 3.5R)
  3. Frame viewport at M87-like angle (near side bright below, far side wraps over).
  4. Save level.
"""
import unreal, math

# ── constants ─────────────────────────────────────────────────────────────────
CENTER    = unreal.Vector(-620000.0, 0.0, 230000.0)
HOLE_R    = 13000.0
HFOV_DEG  = 90.0
ASPECT    = 1280.0 / 720.0           # matches screenshot.py
# Einstein ring = EINSTEIN_MULT × apparent shadow radius (screen-height units)
EINSTEIN_MULT = 2.5
SHADOW_MULT   = 1.05                 # event-horizon dark disk, slightly > core

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_PPLensing2'
FULL     = f'{MAT_PATH}/{MAT_NAME}'

mel  = unreal.MaterialEditingLibrary
eas  = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues  = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les  = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# ── 1. frame camera (slightly above+right of disk equatorial plane) ───────────
# BH disk normal is mostly +Z (0.847) slightly +X (0.532).  Viewing from +X,
# slightly above the BH gives a clean asymmetric ellipse — near side (bottom)
# Doppler-bright, far side wrapped over via lensing.
cam_pos = unreal.Vector(CENTER.x + 175000, CENTER.y + 15000, CENTER.z + 28000)
d       = unreal.Vector(CENTER.x - cam_pos.x,
                        CENTER.y - cam_pos.y,
                        CENTER.z - cam_pos.z)
yaw   = math.degrees(math.atan2(d.y, d.x))
pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x*d.x + d.y*d.y)))
ues.set_level_viewport_camera_info(cam_pos, unreal.Rotator(0.0, pitch, yaw))
les.editor_invalidate_viewports()
print(f'Camera: pos={cam_pos}  yaw={yaw:.1f}  pitch={pitch:.1f}')

# ── 2. compute BH screen UV + radii ───────────────────────────────────────────
loc, rot = ues.get_level_viewport_camera_info()
fwd = rot.get_forward_vector()
rgt = rot.get_right_vector()
up  = rot.get_up_vector()

w       = unreal.Vector(CENTER.x-loc.x, CENTER.y-loc.y, CENTER.z-loc.z)
depth   = w.x*fwd.x + w.y*fwd.y + w.z*fwd.z
x_cam   = w.x*rgt.x + w.y*rgt.y + w.z*rgt.z
y_cam   = w.x*up.x  + w.y*up.y  + w.z*up.z
tan_h   = math.tan(math.radians(HFOV_DEG) * 0.5)
tan_v   = tan_h / ASPECT

if depth <= 1.0:
    print('WARNING: BH behind camera, setting Strength=0')
    cx, cy, R, shadowR, strength = 0.5, 0.5, 0.10, 0.06, 0.0
else:
    cx       = 0.5 + 0.5 * (x_cam / depth) / tan_h
    cy       = 0.5 - 0.5 * (y_cam / depth) / tan_v
    apparent = 0.5 * (HOLE_R / depth) / tan_v
    R        = apparent * EINSTEIN_MULT
    shadowR  = apparent * SHADOW_MULT
    strength = 1.0
    print(f'BH screen UV=({cx:.3f},{cy:.3f})  depth={depth:.0f}  '
          f'apparent={apparent:.4f}  EinsteinR={R:.4f}  ShadowR={shadowR:.4f}')

# ── 3. update MPC_BlackHole scalars ──────────────────────────────────────────
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')

def set_scalar(mpc, name, value):
    """Set (add or update) a scalar in an MPC asset."""
    existing = list(mpc.get_editor_property('scalar_parameters'))
    updated  = [sp for sp in existing
                if str(sp.get_editor_property('parameter_name')) != name]
    sp = unreal.CollectionScalarParameter()
    sp.set_editor_property('parameter_name', name)
    sp.set_editor_property('default_value', float(value))
    updated.append(sp)
    mpc.set_editor_property('scalar_parameters', updated)

set_scalar(mpc, 'BH_ScreenPosition_X', cx)
set_scalar(mpc, 'BH_ScreenPosition_Y', cy)
set_scalar(mpc, 'BH_ScreenRadius',     R)
set_scalar(mpc, 'BH_ShadowRadius',     shadowR)
set_scalar(mpc, 'BH_LensStrength',     strength)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
print('MPC_BlackHole updated.')

# ── 4. rebuild M_PPLensing2 in-place with improved lens code ──────────────────
mat = unreal.EditorAssetLibrary.load_asset(FULL) if \
      unreal.EditorAssetLibrary.does_asset_exist(FULL) else None
if mat is None:
    factory = unreal.MaterialFactoryNew()
    at      = unreal.AssetToolsHelpers.get_asset_tools()
    mat     = at.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)
else:
    mel.delete_all_material_expressions(mat)

mat.set_editor_property('material_domain',      unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',
                        unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)

def mpc_scalar(name, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, x, y)
    n.set_editor_property('collection',       mpc)
    n.set_editor_property('parameter_name',   unreal.Name(name))
    return n

cx_n  = mpc_scalar('BH_ScreenPosition_X', -1100, -240)
cy_n  = mpc_scalar('BH_ScreenPosition_Y', -1100, -160)
sr_n  = mpc_scalar('BH_ScreenRadius',     -1100,  -80)
shr_n = mpc_scalar('BH_ShadowRadius',     -1100,    0)
st_n  = mpc_scalar('BH_LensStrength',     -1100,   80)

uv_n  = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 200)

LENS_CODE = (
    "float2 C = float2(Cx, Cy);\n"
    "float aspect = View.ViewSizeAndInvSize.x * View.ViewSizeAndInvSize.w;\n"
    "float2 d = UV - C; d.x *= aspect;\n"
    "float r = length(d);\n"
    "float2 dir = (r > 1e-5) ? d / r : float2(0.0, 1.0);\n"
    "\n"
    "// Point-mass lens: r -> r - R^2/r (clamped to prevent UV inversion at center)\n"
    "float bend = (R * R) / max(r, R * 0.01);\n"
    "float rb = max(r * 0.01, r - bend * Strength);\n"
    "float2 sd = dir * rb; sd.x /= aspect;\n"
    "float2 uvL = C + sd;\n"
    "\n"
    "// Buffer UV fix: viewport UV != buffer UV in PIE (GPU buffer is padded)\n"
    "float2 bufScale = View.ViewSizeAndInvSize.xy * View.BufferSizeAndInvSize.zw;\n"
    "float3 passthrough = SceneTextureLookup(UV * bufScale, 14, false).rgb;\n"
    "\n"
    "// OOB guard: use passthrough instead of clamped-edge smear\n"
    "float inScreen = (uvL.x > 0.001 && uvL.x < 0.999 &&\n"
    "                  uvL.y > 0.001 && uvL.y < 0.999) ? 1.0 : 0.0;\n"
    "float3 lensed = SceneTextureLookup(clamp(uvL, 0.0, 1.0) * bufScale, 14, false).rgb;\n"
    "float3 col = lerp(passthrough, lensed, inScreen);\n"
    "\n"
    "// Far-field fade: smooth return to pristine background beyond 3.5*R\n"
    "float NearR = R * 1.2;\n"
    "float FarR  = R * 3.5;\n"
    "float fall  = saturate((FarR - r) / max(FarR - NearR, 1e-4));\n"
    "col = lerp(passthrough, col, fall * saturate(Strength));\n"
    "\n"
    "// Shadow mask: dark event horizon (photon capture sphere)\n"
    "float shadow = smoothstep(ShadowR * 0.82, ShadowR, r);\n"
    "col *= lerp(1.0, shadow, saturate(Strength));\n"
    "\n"
    "return col;\n"
)

lens_n = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -600, 0)
lens_n.set_editor_property('description',   'PPGravLens_v2')
lens_n.set_editor_property('output_type',   unreal.CustomMaterialOutputType.CMOT_FLOAT3)
lens_n.set_editor_property('code',          LENS_CODE)

for nm in ['UV', 'Cx', 'Cy', 'R', 'ShadowR', 'Strength']:
    ci = unreal.CustomInput()
    ci.set_editor_property('input_name', unreal.Name(nm))
    lens_n.set_editor_property('inputs', list(lens_n.get_editor_property('inputs')) + [ci])

mel.connect_material_expressions(uv_n,  '', lens_n, 'UV')
mel.connect_material_expressions(cx_n,  '', lens_n, 'Cx')
mel.connect_material_expressions(cy_n,  '', lens_n, 'Cy')
mel.connect_material_expressions(sr_n,  '', lens_n, 'R')
mel.connect_material_expressions(shr_n, '', lens_n, 'ShadowR')
mel.connect_material_expressions(st_n,  '', lens_n, 'Strength')
mel.connect_material_property(lens_n, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Rebuilt {FULL} with shadow mask + OOB guard + far-field fade.')

# ── 5. ensure M_PPLensing2 is attached to PPV_DeepSpace ───────────────────────
ppv = next((a for a in eas.get_all_level_actors()
            if a.get_actor_label() == 'PPV_DeepSpace'), None)
if ppv:
    settings = ppv.get_editor_property('settings')
    existing = list(settings.get_editor_property('weighted_blendables')
                              .get_editor_property('array'))
    already  = any(b.get_editor_property('object') == mat for b in existing)
    if not already:
        wb = unreal.WeightedBlendable()
        wb.set_editor_property('weight', 1.0)
        wb.set_editor_property('object', mat)
        blendables = unreal.WeightedBlendables()
        blendables.set_editor_property('array', existing + [wb])
        settings.set_editor_property('weighted_blendables', blendables)
        ppv.set_editor_property('settings', settings)
        print('Attached M_PPLensing2 to PPV_DeepSpace.')
    else:
        print('M_PPLensing2 already attached to PPV_DeepSpace.')
else:
    print('WARNING: PPV_DeepSpace not found.')

les.save_current_level()
print('Level saved. Open PIE or look at viewport — lensing should now be active.')
print(f'To tweak: edit EINSTEIN_MULT ({EINSTEIN_MULT}) / SHADOW_MULT ({SHADOW_MULT}) at top of script.')
