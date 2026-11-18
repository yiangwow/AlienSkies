"""Black hole 3D pass v2.

Fixes from v1 viewport review:
  - Camera pulled to 335k so the disk box edges don't dominate the frame.
  - Lensing: allow rb to go NEGATIVE (the far-side Einstein arc requires it).
    The old max(r*0.01, ...) clamp prevented negative rb and killed the arc.
    Now only guard against r=0 singularity; negative rb flips the sample dir
    so the far side of the disk appears wrapped over the shadow.
  - Shadow mask + OOB guard + far-field fade retained.
"""
import unreal, math

CENTER   = unreal.Vector(-620000.0, 0.0, 230000.0)
HOLE_R   = 13000.0
HFOV_DEG = 90.0
ASPECT   = 1280.0 / 720.0

# Lensing params
EINSTEIN_MULT = 2.5    # Einstein ring radius = EINSTEIN_MULT × apparent hole radius
SHADOW_MULT   = 1.05   # shadow disk radius   = SHADOW_MULT   × apparent hole radius

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_PPLensing2'
FULL     = f'{MAT_PATH}/{MAT_NAME}'

mel = unreal.MaterialEditingLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# ── 1. frame camera at ~335k — disk reads as a clean ellipse, not a wall ──────
offset  = unreal.Vector(330000, 20000, 50000)
cam_pos = unreal.Vector(CENTER.x + offset.x, CENTER.y + offset.y, CENTER.z + offset.z)
d       = unreal.Vector(CENTER.x - cam_pos.x, CENTER.y - cam_pos.y, CENTER.z - cam_pos.z)
yaw   = math.degrees(math.atan2(d.y, d.x))
pitch = math.degrees(math.atan2(d.z, math.sqrt(d.x*d.x + d.y*d.y)))
ues.set_level_viewport_camera_info(cam_pos, unreal.Rotator(0.0, pitch, yaw))
les.editor_invalidate_viewports()
dist = math.sqrt(offset.x**2 + offset.y**2 + offset.z**2)
print(f'Camera at distance={dist:.0f}  pos={cam_pos}  yaw={yaw:.1f}  pitch={pitch:.1f}')

# ── 2. compute BH screen UV + radii from new camera pose ──────────────────────
loc, rot = ues.get_level_viewport_camera_info()
fwd = rot.get_forward_vector()
rgt = rot.get_right_vector()
up  = rot.get_up_vector()

w     = unreal.Vector(CENTER.x-loc.x, CENTER.y-loc.y, CENTER.z-loc.z)
depth = w.x*fwd.x + w.y*fwd.y + w.z*fwd.z
x_c   = w.x*rgt.x + w.y*rgt.y + w.z*rgt.z
y_c   = w.x*up.x  + w.y*up.y  + w.z*up.z
tan_h = math.tan(math.radians(HFOV_DEG) * 0.5)
tan_v = tan_h / ASPECT

if depth <= 1.0:
    print('WARNING: BH behind camera, Strength=0')
    cx, cy, R, shadowR, strength = 0.5, 0.5, 0.10, 0.06, 0.0
else:
    cx       = 0.5 + 0.5 * (x_c / depth) / tan_h
    cy       = 0.5 - 0.5 * (y_c / depth) / tan_v
    apparent = 0.5 * (HOLE_R / depth) / tan_v
    R        = apparent * EINSTEIN_MULT
    shadowR  = apparent * SHADOW_MULT
    strength = 1.0
    print(f'BH screen UV=({cx:.3f},{cy:.3f})  depth={depth:.0f}  '
          f'apparent={apparent:.4f}  EinsteinR={R:.4f}  ShadowR={shadowR:.4f}')

# ── 3. update MPC_BlackHole ────────────────────────────────────────────────────
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')

def set_scalar(mpc, name, value):
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
print('MPC updated.')

# ── 4. rebuild M_PPLensing2 — allow negative rb for Einstein arc ──────────────
mat = unreal.EditorAssetLibrary.load_asset(FULL) if \
      unreal.EditorAssetLibrary.does_asset_exist(FULL) else None
if mat is None:
    factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
              MAT_NAME, MAT_PATH, unreal.Material, factory)
else:
    mel.delete_all_material_expressions(mat)

mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',
                        unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)

def mpc_scalar(name, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, x, y)
    n.set_editor_property('collection',     mpc)
    n.set_editor_property('parameter_name', unreal.Name(name))
    return n

cx_n  = mpc_scalar('BH_ScreenPosition_X', -1100, -240)
cy_n  = mpc_scalar('BH_ScreenPosition_Y', -1100, -160)
sr_n  = mpc_scalar('BH_ScreenRadius',     -1100,  -80)
shr_n = mpc_scalar('BH_ShadowRadius',     -1100,    0)
st_n  = mpc_scalar('BH_LensStrength',     -1100,   80)
uv_n  = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 200)

# KEY FIX: rb is allowed to go negative here.
# Negative rb means the sample direction flips → samples from the antipodal side
# of the BH center, pulling the far-side disk gas up/over the shadow (Einstein arc).
# Only guard is rSafe = max(r, ShadowR*0.5) to avoid the r=0 singularity.
# The center guard (smoothstep) fades lensing to passthrough near center so there's
# no hard artifact; the shadow mask then darkens the event-horizon region.
LENS_CODE = (
    "float2 C = float2(Cx, Cy);\n"
    "float aspect = View.ViewSizeAndInvSize.x * View.ViewSizeAndInvSize.w;\n"
    "float2 d = UV - C; d.x *= aspect;\n"
    "float r = length(d);\n"
    "float2 dir = (r > 1e-5) ? d / r : float2(0.0, 1.0);\n"
    "\n"
    "// Buffer UV fix (PIE viewport padding)\n"
    "float2 bufScale = View.ViewSizeAndInvSize.xy * View.BufferSizeAndInvSize.zw;\n"
    "float3 passthrough = SceneTextureLookup(UV * bufScale, 14, false).rgb;\n"
    "\n"
    "// Point-mass lens — rb ALLOWED to go negative for far-side Einstein arc\n"
    "float rSafe = max(r, ShadowR * 0.5);   // guard only against r=0 singularity\n"
    "float bend  = (R * R) / rSafe;\n"
    "float rb    = r - bend * Strength;     // negative => sample flips to antipodal side\n"
    "float2 sd   = dir * rb; sd.x /= aspect;\n"
    "float2 uvL  = C + sd;\n"
    "\n"
    "// OOB guard: passthrough when lensed UV leaves screen\n"
    "float inScreen = (uvL.x > 0.001 && uvL.x < 0.999 &&\n"
    "                  uvL.y > 0.001 && uvL.y < 0.999) ? 1.0 : 0.0;\n"
    "float3 lensed = SceneTextureLookup(clamp(uvL, 0.0, 1.0) * bufScale, 14, false).rgb;\n"
    "\n"
    "// Center guard: smooth fade to passthrough near r=0 to avoid instability\n"
    "float cGuard = smoothstep(0.0, ShadowR * 1.3, r);\n"
    "float3 col   = lerp(passthrough, lerp(passthrough, lensed, inScreen), cGuard);\n"
    "\n"
    "// Far-field fade: return to pristine space beyond 3.5*R\n"
    "float FarR = R * 3.5;\n"
    "float fall = saturate((FarR - r) / max(FarR - R * 1.2, 1e-4));\n"
    "col = lerp(passthrough, col, fall * saturate(Strength));\n"
    "\n"
    "// Shadow mask: event-horizon dark disk\n"
    "float shadow = smoothstep(ShadowR * 0.80, ShadowR, r);\n"
    "col *= lerp(1.0, shadow, saturate(Strength));\n"
    "\n"
    "return col;\n"
)

lens_n = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -600, 0)
lens_n.set_editor_property('description', 'PPGravLens_v3_EinsteinArc')
lens_n.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
lens_n.set_editor_property('code', LENS_CODE)

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
print(f'Rebuilt {FULL}: rb can go negative → Einstein arc enabled.')

# ── 5. verify PPV attachment ───────────────────────────────────────────────────
ppv = next((a for a in eas.get_all_level_actors()
            if a.get_actor_label() == 'PPV_DeepSpace'), None)
if ppv:
    settings = ppv.get_editor_property('settings')
    existing = list(settings.get_editor_property('weighted_blendables')
                              .get_editor_property('array'))
    already = any(b.get_editor_property('object') == mat for b in existing)
    if not already:
        wb = unreal.WeightedBlendable()
        wb.set_editor_property('weight', 1.0)
        wb.set_editor_property('object', mat)
        blendables = unreal.WeightedBlendables()
        blendables.set_editor_property('array', existing + [wb])
        settings.set_editor_property('weighted_blendables', blendables)
        ppv.set_editor_property('settings', settings)
        print('Attached to PPV_DeepSpace.')
    else:
        print('PPV attachment OK.')
else:
    print('WARNING: PPV_DeepSpace not found.')

les.save_current_level()
print('Done. Check viewport — Einstein arc should now appear between shadow edge and outer disk.')
print(f'EinsteinR={R:.4f} ShadowR={shadowR:.4f} — the arc lives between these two radii.')
