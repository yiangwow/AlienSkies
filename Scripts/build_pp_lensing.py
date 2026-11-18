"""M_PPLensing — FULL-SCREEN post-process gravitational lensing for the black hole.

The localized M_Lensing sphere only gives the Einstein ring + subtle refraction; it
cannot WRAP the disk over the shadow. This post-process material screen-bends the UVs
around the hole's projected screen position using the point-mass lens equation
(sample scene color at radius  r - R^2/r  around the center). Letting that term fold
through center pulls the far side of the disk UP/DOWN over the shadow (the iconic M87
arc) and bends background stars around the hole.

Reads MPC_BlackHole scalars (driven per-frame by SceneDirector at runtime, or by
set_bh_screen.py for editor-screenshot iteration):
  BH_ScreenPosition_X / _Y  -> hole center in screen UV (0..1)
  BH_ScreenRadius           -> Einstein radius in screen-HEIGHT units
  BH_ShadowRadius           -> event-horizon dark disk radius (screen-height units)
  BH_LensStrength           -> 0..1 master strength (0 when hole off-screen/behind)

Attaches as a blendable on the unbound PPV_DeepSpace (SceneCapture honors it, so it
shows in screenshot.py). Idempotent: deletes + rebuilds the material each run.
"""
import unreal

MAT_PATH = '/Game/AlienSkies/Materials'
NAME = 'M_PPLensing2'
FULL = f'{MAT_PATH}/{NAME}'
mel = unreal.MaterialEditingLibrary

# ---------- 0: ensure MPC scalars exist (match the C++ SceneDirector naming) ----------
mpc_bh = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')


def ensure_scalar(mpc, name, default):
    existing = list(mpc.get_editor_property('scalar_parameters'))
    for sp in existing:
        if str(sp.get_editor_property('parameter_name')) == name:
            return False
    sp = unreal.CollectionScalarParameter()
    sp.set_editor_property('parameter_name', name)
    sp.set_editor_property('default_value', float(default))
    existing.append(sp)
    mpc.set_editor_property('scalar_parameters', existing)
    return True


added = []
for n, d in [('BH_ScreenPosition_X', 0.5), ('BH_ScreenPosition_Y', 0.5),
             ('BH_ScreenRadius', 0.10), ('BH_ShadowRadius', 0.06),
             ('BH_LensStrength', 0.0)]:
    if ensure_scalar(mpc_bh, n, d):
        added.append(n)
if added:
    unreal.EditorAssetLibrary.save_loaded_asset(mpc_bh)
print('MPC scalars added:', added or '(none — already present)')

# ---------- 1: build the post-process material ----------
# Rebuild the graph IN PLACE (delete_all_material_expressions) rather than deleting the
# asset — once it's referenced by the PPV blendable, delete_asset fails and create
# returns None. In-place rebuild keeps the PPV reference valid across re-runs.
mat = unreal.EditorAssetLibrary.load_asset(FULL) if unreal.EditorAssetLibrary.does_asset_exist(FULL) else None
if mat is not None:
    mel.delete_all_material_expressions(mat)
else:
    factory = unreal.MaterialFactoryNew()
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(NAME, MAT_PATH, unreal.Material, factory)
mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location', unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)


def mpc_scalar(name, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, x, y)
    n.set_editor_property('collection', mpc_bh)
    n.set_editor_property('parameter_name', unreal.Name(name))
    return n


cx = mpc_scalar('BH_ScreenPosition_X', -1100, -200)
cy = mpc_scalar('BH_ScreenPosition_Y', -1100, -120)
sr = mpc_scalar('BH_ScreenRadius', -1100, -40)
shr = mpc_scalar('BH_ShadowRadius', -1100, 40)
st = mpc_scalar('BH_LensStrength', -1100, 120)

# Screen UV (in PP domain, TexCoord0 = viewport UV)
uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 240)

# SceneTexture Bind: connecting this makes SceneTextureLookup available inside the Custom node.
# Without it the function is undeclared and the shader fails to compile.
st_bind = mel.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -1100, 320)
st_bind.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)

lens = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -650, 0)
lens.set_editor_property('description', 'PPGravLensing')
lens.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
lens.set_editor_property('code',
"float2 C = float2(Cx, Cy);\n"
"float aspect = View.ViewSizeAndInvSize.x * View.ViewSizeAndInvSize.w;\n"
"float2 d = UV - C; d.x *= aspect;\n"
"float r = length(d);\n"
"float2 dir = (r > 1e-5) ? d / r : float2(0.0, 1.0);\n"
"float bend = (R * R) / max(r, R * 0.01);\n"
"float rb = max(r * 0.01, r - bend * Strength);\n"  # clamp: no UV inversion at center
"float2 sd = dir * rb; sd.x /= aspect;\n"
"float2 uvL = C + sd;\n"
# FIX: viewport UV -> buffer UV so edge pixels don't sample black padding in PIE
"float2 bufScale = View.ViewSizeAndInvSize.xy * View.BufferSizeAndInvSize.zw;\n"
"float3 passthrough = SceneTextureLookup(UV * bufScale, 14, false).rgb;\n"
"float3 lensed = SceneTextureLookup(clamp(uvL, 0.0, 1.0) * bufScale, 14, false).rgb;\n"
# OOB: clamped sample smears the frame edge -> fall back to passthrough outside [0,1]
"float oob = (uvL.x >= 0.0 && uvL.x <= 1.0 && uvL.y >= 0.0 && uvL.y <= 1.0) ? 1.0 : 0.0;\n"
# Inner guard fades to zero at center (unstable rb region)
"float guard = smoothstep(0.0, R, r);\n"
# Far-field falloff: lens fades back to passthrough beyond 4*R so screen edges stay clean
"float NearR = R * 1.5;\n"
"float FarR  = R * 4.0;\n"
"float fall  = saturate((FarR - r) / max(FarR - NearR, 1e-4));\n"
"float3 col = lerp(passthrough, lensed, guard * fall * oob);\n"
"return lerp(passthrough, col, saturate(Strength));\n"
)
inputs = []
for nm in ['UV', 'Cx', 'Cy', 'R', 'ShadowR', 'Strength', 'Bind']:
    ci = unreal.CustomInput()
    ci.set_editor_property('input_name', unreal.Name(nm))
    inputs.append(ci)
lens.set_editor_property('inputs', inputs)

mel.connect_material_expressions(uv, '', lens, 'UV')
mel.connect_material_expressions(cx, '', lens, 'Cx')
mel.connect_material_expressions(cy, '', lens, 'Cy')
mel.connect_material_expressions(sr, '', lens, 'R')
mel.connect_material_expressions(shr, '', lens, 'ShadowR')
mel.connect_material_expressions(st, '', lens, 'Strength')
mel.connect_material_expressions(st_bind, '', lens, 'Bind')  # declares SceneTextureLookup
mel.connect_material_property(lens, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL}')

# ---------- 2: attach as a blendable on PPV_DeepSpace ----------
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ppv = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'PPV_DeepSpace':
        ppv = a
        break
if ppv:
    settings = ppv.get_editor_property('settings')
    wb = unreal.WeightedBlendable()
    wb.set_editor_property('weight', 1.0)
    wb.set_editor_property('object', mat)
    blendables = unreal.WeightedBlendables()
    # keep any existing blendables that aren't our lensing material
    existing = list(settings.get_editor_property('weighted_blendables').get_editor_property('array'))
    keep = [b for b in existing if b.get_editor_property('object') != mat]
    blendables.set_editor_property('array', keep + [wb])
    settings.set_editor_property('weighted_blendables', blendables)
    ppv.set_editor_property('settings', settings)
    les.save_current_level()
    print('Attached M_PPLensing to PPV_DeepSpace and saved level.')
else:
    print('WARNING: PPV_DeepSpace not found — material built but not attached.')
