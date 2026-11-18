"""M_SpiralGalaxy — a procedural spiral galaxy disc for the TTGL look.

Applied to a flat plane/disc mesh. Reads UV (0..1, centered at 0.5).
- Logarithmic spiral arms (2-4 arms) via angle + log(radius) banding
- Bright hot core (radial falloff, white-blue)
- Arm color gradient: blue-white inner → warm outer
- Dust noise breakup
- Soft circular edge falloff so the square plane reads as a disc
- Emissive output, Unlit, Additive blend so it glows against black space

Parameters (instanceable): ArmCount, SpinTightness, CoreColor, ArmColor, Brightness, Rotation
"""
import unreal

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_SpiralGalaxy'
FULL = f'{MAT_PATH}/{MAT_NAME}'

# Rebuild IN PLACE — keeps existing MIDs on Galaxy_ actors valid.
# delete_asset would orphan every galaxy's MaterialInstanceDynamic → opaque gray blocks.
mel = unreal.MaterialEditingLibrary
if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    mat = unreal.load_asset(FULL)
    mel.delete_all_material_expressions(mat)
else:
    factory = unreal.MaterialFactoryNew()
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
# Additive: glowing emissive adds to space, dark areas contribute nothing.
# No opacity mask needed, no translucency sort issues between overlapping galaxies.
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)


# --- Scalar/vector parameters ---
def scalar(name, val, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', float(val))
    return n

def vec(name, color, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, x, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', color)
    return n

p_arms      = scalar('ArmCount', 2.0, -1300, -200)
p_tight     = scalar('SpinTightness', 5.0, -1300, -120)
p_bright    = scalar('Brightness', 8.0, -1300, -40)
p_rotation  = scalar('Rotation', 0.0, -1300, 40)
p_rotspeed  = scalar('RotationSpeed', 0.05, -1300, 360)
p_emix      = scalar('EllipticalMix', 0.0, -1300, 440)    # 0=spiral, 1=smooth elliptical
p_core      = vec('CoreColor', unreal.LinearColor(0.7, 0.85, 1.0, 1.0), -1300, 140)
p_armcol    = vec('ArmColor', unreal.LinearColor(1.0, 0.6, 0.35, 1.0), -1300, 260)

# Animated rotation: Rotation + Time * RotationSpeed  -> feeds the spiral phase.
_time = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -1100, 360)
_spin = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -950, 360)
mel.connect_material_expressions(_time, '', _spin, 'A')
mel.connect_material_expressions(p_rotspeed, '', _spin, 'B')
_rotsum = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -800, 200)
mel.connect_material_expressions(p_rotation, '', _rotsum, 'A')
mel.connect_material_expressions(_spin, '', _rotsum, 'B')

# --- TexCoord ---
uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 400)

# --- HLSL galaxy node ---
galaxy = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -700, 0)
galaxy.set_editor_property('description', 'SpiralGalaxy')
galaxy.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
galaxy.set_editor_property('code', """
float2 p = UV - 0.5;
float r = length(p) * 2.0;          // 0 at center, 1 at edge
float ang = atan2(p.y, p.x) + Rotation;

if (r > 1.0) return float3(0,0,0);   // never render past the plane's side-edge (r=1.0)

#define H2(v) frac(sin(dot(v, float2(127.1, 311.7))) * 43758.5453)

// ===== Spiral flow space =====
// Sample noise in (spiral-phase, radius) so all detail streaks ALONG the arms,
// giving the swept turbulent-gas look (ref: M87 accretion disk filaments).
float phase = ang * ArmCount + log(r + 0.06) * SpinTightness;
float2 flow = float2(phase * 0.5, r * 4.5);

// ===== Domain warp (2 octaves) — bends the filaments into swirls =====
float2 warp = float2(0.0, 0.0);
{
    float2 q = flow * 0.7 + 3.1;
    float amp = 1.0;
    [unroll]
    for (int i = 0; i < 2; i++)
    {
        float2 ip = floor(q), fp = frac(q); fp = fp*fp*(3.0-2.0*fp);
        float a=H2(ip), b=H2(ip+float2(1,0)), c=H2(ip+float2(0,1)), d=H2(ip+float2(1,1));
        float n = lerp(lerp(a,b,fp.x), lerp(c,d,fp.x), fp.y);
        float a2=H2(ip+19.3), b2=H2(ip+float2(1,0)+19.3), c2=H2(ip+float2(0,1)+19.3), d2=H2(ip+float2(1,1)+19.3);
        float n2 = lerp(lerp(a2,b2,fp.x), lerp(c2,d2,fp.x), fp.y);
        warp += (float2(n, n2) - 0.5) * amp;
        q *= 2.0; amp *= 0.5;
    }
}

// ===== Fine turbulent gas: 6-octave fbm in warped spiral space =====
float gas = 0.0;
{
    float2 q = flow + warp * 1.6;
    float amp = 0.5;
    [unroll]
    for (int i = 0; i < 6; i++)
    {
        float2 ip = floor(q), fp = frac(q); fp = fp*fp*(3.0-2.0*fp);
        float a=H2(ip), b=H2(ip+float2(1,0)), c=H2(ip+float2(0,1)), d=H2(ip+float2(1,1));
        gas += lerp(lerp(a,b,fp.x), lerp(c,d,fp.x), fp.y) * amp;
        q = q * 2.0 + 1.7; amp *= 0.5;
    }
}

// SHARP spiral arms — narrow bright bands, genuine dark void between them.
// pow(max(0,cos),5) goes to zero between arms so inter-arm space is truly black.
float arm = pow(max(0.0, cos(phase)), 5.0);
float radial = smoothstep(1.0, 0.02, r);

// Gas density gated on arm region: bright IN arms, near-zero in the void.
float density = saturate((gas - 0.30) * 3.5) * arm * radial;
density = pow(density, 1.5);   // contrast — filaments pop, weak gas disappears

// Faint inter-arm haze so the disc isn't 100% black between arms
float haze = saturate(gas * 0.45 - 0.08) * (1.0 - arm * 0.8) * radial * 0.10;

// Dust lanes threading through the bright arm gas
float lane = 1.0 - 0.55 * (smoothstep(0.30, 0.44, gas) * (1.0 - smoothstep(0.44, 0.58, gas)));

// ===== Star field — visible in arm regions AND faint scatter across the disc =====
float stars = 0.0;
[unroll]
for (int s = 0; s < 4; s++)
{
    float freq = 46.0 * pow(2.0, (float)s);
    float2 g = p * freq;
    float2 gi = floor(g);
    float h = H2(gi);
    if (h > 0.82 - 0.02 * s)
    {
        float2 jit = float2(h, frac(h * 53.7)) - 0.5;
        float2 d = frac(g) - 0.5 - jit * 0.7;
        stars += exp(-dot(d, d) * 70.0) * frac(h * 91.7) / (1.0 + 0.3 * s);
    }
}
// Dense in arms, still faintly visible in voids
stars *= (arm * 1.6 + 0.20) * radial;

// EllipticalMix: 0=spiral arms, 1=smooth glowing orb (no arms)
float elliptical = exp(-r * r * 5.5) * 0.9 * radial;
density = lerp(density, elliptical, EllipticalMix);
stars   = lerp(stars,   elliptical * 0.4, EllipticalMix); // ellipticals have smooth star spread

// ===== Core: tight blazing nucleus + small tight bulge =====
float core  = exp(-r * r * 80.0);
float bulge = exp(-r * r * 16.0) * 0.28;

// ===== Compose =====
float3 col = float3(0,0,0);
col += ArmColor * (density + haze) * lane;                        // arm gas (primary color driver)
col += lerp(float3(1.0, 0.95, 0.82), ArmColor * 2.0, 0.55) * stars; // stars tinted toward ArmColor
col += CoreColor * (core * 0.7 + bulge);     // blazing nucleus
// Inner warm tint toward core color
col = lerp(col, col * CoreColor * 1.3, smoothstep(0.45, 0.0, r) * 0.5);

col *= smoothstep(0.95, 0.65, r);            // fade to 0 well inside plane edge — no square seams
return col * Brightness;
""")
inp = unreal.CustomInput(); inp.set_editor_property('input_name', 'UV')
ang_in = unreal.CustomInput(); ang_in.set_editor_property('input_name', 'Rotation')
arm_in = unreal.CustomInput(); arm_in.set_editor_property('input_name', 'ArmCount')
tight_in = unreal.CustomInput(); tight_in.set_editor_property('input_name', 'SpinTightness')
bright_in = unreal.CustomInput(); bright_in.set_editor_property('input_name', 'Brightness')
core_in = unreal.CustomInput(); core_in.set_editor_property('input_name', 'CoreColor')
armcol_in = unreal.CustomInput(); armcol_in.set_editor_property('input_name', 'ArmColor')
emix_in = unreal.CustomInput(); emix_in.set_editor_property('input_name', 'EllipticalMix')
galaxy.set_editor_property('inputs', [inp, ang_in, arm_in, tight_in, bright_in, core_in, armcol_in, emix_in])

mel.connect_material_expressions(uv, '', galaxy, 'UV')
mel.connect_material_expressions(_rotsum, '', galaxy, 'Rotation')  # animated (Rotation + Time*RotationSpeed)
mel.connect_material_expressions(p_arms, '', galaxy, 'ArmCount')
mel.connect_material_expressions(p_tight, '', galaxy, 'SpinTightness')
mel.connect_material_expressions(p_bright, '', galaxy, 'Brightness')
mel.connect_material_expressions(p_core, '', galaxy, 'CoreColor')
mel.connect_material_expressions(p_armcol, '', galaxy, 'ArmColor')
mel.connect_material_expressions(p_emix,   '', galaxy, 'EllipticalMix')

mel.connect_material_property(galaxy, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
# Additive blend needs no opacity mask — dark emissive simply adds nothing.

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL}')
