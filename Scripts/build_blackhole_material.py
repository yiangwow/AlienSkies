"""M_AccretionDisk — the accretion disk of a black hole, on a flat plane.

Reads centered UV (r 0..1):
- r < InnerRadius -> the ISCO void (transparent/black, you see the hole behind)
- disk band InnerRadius..1 with a temperature gradient:
    inner = blue-white (hottest) -> orange -> dim red (outer)
- Keplerian shear: inner rings rotate faster than outer (Time-driven, angular vel ~ r^-1.5)
- Turbulent gas banding via smooth value noise sheared by the rotation
- Additive, unlit, two-sided. Very bright -> drives bloom.

Params: InnerRadius, Brightness, RotationSpeed, DiskTint(core/mid/outer baked).
"""
import unreal

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_AccretionDisk'
FULL = f'{MAT_PATH}/{MAT_NAME}'

if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    unreal.EditorAssetLibrary.delete_asset(FULL)

factory = unreal.MaterialFactoryNew()
at = unreal.AssetToolsHelpers.get_asset_tools()
mat = at.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)

mel = unreal.MaterialEditingLibrary

def scalar(name, val, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property('parameter_name', name); n.set_editor_property('default_value', float(val)); return n

p_inner  = scalar('InnerRadius', 0.32, -1300, -120)
p_bright = scalar('Brightness', 25.0, -1300, -40)
p_rotspd = scalar('RotationSpeed', 0.6, -1300, 40)

# Time * RotationSpeed for the Keplerian shear
_t = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -1100, 120)
_spin = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -950, 90)
mel.connect_material_expressions(_t, '', _spin, 'A')
mel.connect_material_expressions(p_rotspd, '', _spin, 'B')

uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 260)

disk = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -650, 0)
disk.set_editor_property('description', 'AccretionDisk')
disk.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
disk.set_editor_property('code', """
float2 p = UV - 0.5;
float r = length(p) * 2.0;          // 0 center .. 1 edge
float ang = atan2(p.y, p.x);

if (r > 1.0 || r < InnerRadius) return float3(0,0,0);   // outside disk or inside ISCO void

#define H2(v) frac(sin(dot(v, float2(127.1, 311.7))) * 43758.5453)

float band = saturate((r - InnerRadius) / (1.0 - InnerRadius));

// Keplerian shear: inner orbits much faster (angVel ~ r^-1.5).
float angVel = pow(max(r, 0.045), -1.5);
float sweep = ang + Spin * angVel;

// ---- domain-warped turbulent gas in (sweep, band) -> fine swirling filaments ----
float2 base = float2(sweep * 0.9, band * 11.0);
float2 warp = float2(0,0);
{
    float2 q = base * 0.8 + 2.0; float a = 1.0;
    [unroll]
    for (int i = 0; i < 2; i++) {
        float2 ip=floor(q), fp=frac(q); fp=fp*fp*(3.0-2.0*fp);
        float n  = lerp(lerp(H2(ip),H2(ip+float2(1,0)),fp.x), lerp(H2(ip+float2(0,1)),H2(ip+float2(1,1)),fp.x), fp.y);
        float n2 = lerp(lerp(H2(ip+9.1),H2(ip+float2(1,0)+9.1),fp.x), lerp(H2(ip+float2(0,1)+9.1),H2(ip+float2(1,1)+9.1),fp.x), fp.y);
        warp += (float2(n,n2)-0.5) * a; q *= 2.0; a *= 0.5;
    }
}
float gas = 0.0; { float2 q = base + warp * 1.4; float a = 0.5;
    [unroll]
    for (int i = 0; i < 6; i++) {
        float2 ip=floor(q), fp=frac(q); fp=fp*fp*(3.0-2.0*fp);
        gas += lerp(lerp(H2(ip),H2(ip+float2(1,0)),fp.x), lerp(H2(ip+float2(0,1)),H2(ip+float2(1,1)),fp.x), fp.y) * a;
        q = q*2.0 + 1.7; a *= 0.5;
    }
}
gas = 0.18 + 1.25 * gas;
gas = pow(saturate(gas), 1.9);                    // high contrast -> crisp visible filaments

// Temperature: BLAZING white-hot inner -> orange -> deep red (M87).
float3 white  = float3(1.0, 0.98, 0.93);
float3 orange = float3(1.0, 0.52, 0.14);
float3 red    = float3(0.85, 0.14, 0.04);
float3 temp = lerp(white, orange, smoothstep(0.0, 0.32, band));
temp = lerp(temp, red, smoothstep(0.32, 1.0, band));

// Brightness profile: concentrate light at the inner edge, soft lips
float profile = pow(1.0 - band, 2.2);
profile *= smoothstep(0.0, 0.035, band);          // soft inner lip
profile *= smoothstep(1.0, 0.70, r);              // soft outer fade

// Blazing inner ring (the white-hot ISCO glow) — modulated by gas so it's not a flat blob
float blaze = exp(-band * band * 30.0) * 0.85 * (0.5 + 0.5*gas);

// Relativistic Doppler beaming: approaching side much brighter
float beam = 0.55 + 0.7 * cos(ang);

float3 col = temp * (profile * gas + blaze) * beam;
return col * Brightness;
""")
ui = unreal.CustomInput(); ui.set_editor_property('input_name','UV')
si = unreal.CustomInput(); si.set_editor_property('input_name','Spin')
ii = unreal.CustomInput(); ii.set_editor_property('input_name','InnerRadius')
bi = unreal.CustomInput(); bi.set_editor_property('input_name','Brightness')
disk.set_editor_property('inputs', [ui, si, ii, bi])
mel.connect_material_expressions(uv, '', disk, 'UV')
mel.connect_material_expressions(_spin, '', disk, 'Spin')
mel.connect_material_expressions(p_inner, '', disk, 'InnerRadius')
mel.connect_material_expressions(p_bright, '', disk, 'Brightness')
mel.connect_material_property(disk, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL}')


# ---- M_BlackHoleCore: pure black, occludes what's behind (the event horizon) ----
CORE = f'{MAT_PATH}/M_BlackHoleCore'
if unreal.EditorAssetLibrary.does_asset_exist(CORE):
    unreal.EditorAssetLibrary.delete_asset(CORE)
cmat = at.create_asset('M_BlackHoleCore', MAT_PATH, unreal.Material, factory)
cmat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
cmat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
black = mel.create_material_expression(cmat, unreal.MaterialExpressionConstant3Vector, -300, 0)
black.set_editor_property('constant', unreal.LinearColor(0,0,0,1))
mel.connect_material_property(black, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(cmat)
unreal.EditorAssetLibrary.save_loaded_asset(cmat)
print(f'Created {CORE}')


# ---- M_PhotonRing: Fresnel emissive glow on a sphere slightly larger than the hole ----
RING = f'{MAT_PATH}/M_PhotonRing'
if unreal.EditorAssetLibrary.does_asset_exist(RING):
    unreal.EditorAssetLibrary.delete_asset(RING)
rmat = at.create_asset('M_PhotonRing', MAT_PATH, unreal.Material, factory)
rmat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
rmat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
rmat.set_editor_property('two_sided', True)
fres = mel.create_material_expression(rmat, unreal.MaterialExpressionFresnel, -500, 0)
fres.set_editor_property('exponent', 5.0)
fres.set_editor_property('base_reflect_fraction', 0.0)
tint = mel.create_material_expression(rmat, unreal.MaterialExpressionConstant3Vector, -500, 200)
tint.set_editor_property('constant', unreal.LinearColor(1.0, 0.75, 0.4, 1.0))  # warm photon glow
mul = mel.create_material_expression(rmat, unreal.MaterialExpressionMultiply, -250, 80)
mul2 = mel.create_material_expression(rmat, unreal.MaterialExpressionMultiply, -100, 80)
strength = mel.create_material_expression(rmat, unreal.MaterialExpressionConstant, -250, 260)
strength.set_editor_property('r', 4.0)
mel.connect_material_expressions(fres, '', mul, 'A')
mel.connect_material_expressions(tint, '', mul, 'B')
mel.connect_material_expressions(mul, '', mul2, 'A')
mel.connect_material_expressions(strength, '', mul2, 'B')
mel.connect_material_property(mul2, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(rmat)
unreal.EditorAssetLibrary.save_loaded_asset(rmat)
print(f'Created {RING}')
