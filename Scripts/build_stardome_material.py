"""Create M_StarDome: an Unlit material that procedurally renders a starfield
on an inverted sphere.

Approach (HLSL custom node):
  - Input: ViewDir = normalize(WorldPosition - CameraPosition) — direction from
    camera through the pixel. For a sphere centered on the camera this is
    effectively the spherical direction of the sky pixel.
  - Cell the unit sphere into a 3D grid, hash each cell, place a star at the
    hashed sub-cell offset, brightness varies by hash.
  - Star color: slight tint variation (warm vs cool stars).
  - Output: emissive float3.
"""
import unreal

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_StarDome'
FULL_PATH = f'{MAT_PATH}/{MAT_NAME}'

# Delete + rebuild fresh. rebuild_scene.py re-applies the material to SM_SkySphere.
if unreal.EditorAssetLibrary.does_asset_exist(FULL_PATH):
    unreal.EditorAssetLibrary.delete_asset(FULL_PATH)

# ---------- Create the asset ----------
factory = unreal.MaterialFactoryNew()
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mat = asset_tools.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)
if not mat:
    raise RuntimeError('Failed to create material')

# Unlit, opaque — we want the stars to be the entire output of the sphere,
# nothing else lit, no fog occlusion.
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
# Two-sided so we can view it from inside a plain uniform sphere (BasicShapes/Sphere),
# which renders the nebula uniformly in all directions (the engine SM_SkySphere mesh
# has structured horizon geometry that produced a smooth band at the bottom).
mat.set_editor_property('two_sided', True)

mel = unreal.MaterialEditingLibrary

# ---------- HLSL star node ----------
star_node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -400, 0)
star_node.set_editor_property('description', 'ProceduralStars')
star_node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
star_node.set_editor_property('code', """
// TTGL cosmic-battlefield backdrop: colored nebula gas + procedural stars.
float3 dir = normalize(ViewDir);
float3 col = float3(0,0,0);

#define HASH3(p) frac(sin(dot(p, float3(127.1, 311.7, 74.7))) * 43758.5453)

// ===================== COLORED NEBULA =====================
// 5-octave fbm value noise over the view direction (higher base freq => finer
// clouds, no large smooth zones forming a 'floor band').
float fbm = 0.0;
float amp = 0.55;
float3 P = dir * 3.4;
[unroll]
for (int o = 0; o < 5; o++)
{
    float3 ip = floor(P);
    float3 fp = frac(P);
    fp = fp * fp * (3.0 - 2.0 * fp);   // smooth weights
    float n000 = HASH3(ip + float3(0,0,0));
    float n100 = HASH3(ip + float3(1,0,0));
    float n010 = HASH3(ip + float3(0,1,0));
    float n110 = HASH3(ip + float3(1,1,0));
    float n001 = HASH3(ip + float3(0,0,1));
    float n101 = HASH3(ip + float3(1,0,1));
    float n011 = HASH3(ip + float3(0,1,1));
    float n111 = HASH3(ip + float3(1,1,1));
    float nz0 = lerp(lerp(n000, n100, fp.x), lerp(n010, n110, fp.x), fp.y);
    float nz1 = lerp(lerp(n001, n101, fp.x), lerp(n011, n111, fp.x), fp.y);
    fbm += lerp(nz0, nz1, fp.z) * amp;
    P *= 2.07;
    amp *= 0.5;
}

// Hue field: higher freq so color varies across the sky (no single-color
// hemisphere). 2-octave for richer mixing.
float hueField = 0.0;
{
    float3 Q = dir * 2.6 + 11.3;
    float hamp = 0.65;
    [unroll]
    for (int hh = 0; hh < 2; hh++)
    {
        float3 ip = floor(Q); float3 fp = frac(Q); fp = fp*fp*(3.0-2.0*fp);
        float a = HASH3(ip+float3(0,0,0)); float b = HASH3(ip+float3(1,0,0));
        float c = HASH3(ip+float3(0,1,0)); float e = HASH3(ip+float3(1,1,0));
        float n001 = HASH3(ip+float3(0,0,1)); float n101 = HASH3(ip+float3(1,0,1));
        float n011 = HASH3(ip+float3(0,1,1)); float n111 = HASH3(ip+float3(1,1,1));
        float z0 = lerp(lerp(a,b,fp.x), lerp(c,e,fp.x), fp.y);
        float z1 = lerp(lerp(n001,n101,fp.x), lerp(n011,n111,fp.x), fp.y);
        hueField += lerp(z0, z1, fp.z) * hamp;
        Q *= 2.3; hamp *= 0.5;
    }
}

// Palette: deep purple / blue / magenta / cyan / green — saturated TTGL colors.
float3 cPurple  = float3(0.30, 0.06, 0.55);
float3 cBlue    = float3(0.05, 0.12, 0.45);
float3 cMagenta = float3(0.55, 0.06, 0.40);
float3 cCyan    = float3(0.05, 0.40, 0.50);
float3 cGreen   = float3(0.10, 0.40, 0.20);

float3 nebColor = lerp(cPurple, cBlue, smoothstep(0.0, 0.35, hueField));
nebColor = lerp(nebColor, cMagenta, smoothstep(0.35, 0.55, hueField));
nebColor = lerp(nebColor, cCyan,    smoothstep(0.55, 0.78, hueField));
nebColor = lerp(nebColor, cGreen,   smoothstep(0.78, 1.0,  hueField));

// Wispy density: ridged detail carves filaments into the smooth clouds.
float density = saturate((fbm - 0.40) * 1.8);
density = pow(density, 1.7);
// High-freq ridged modulation -> wisps/filaments rather than flat blobs
float wisp = abs(frac(fbm * 6.0) - 0.5) * 2.0;     // 0..1 ridges
density *= (0.55 + 0.45 * wisp);

col += nebColor * density * 0.85;                  // dimmer, less poster-paint
// Faint base tint so the void is deep indigo, never pure black
col += float3(0.015, 0.008, 0.035);

// ===================== GALACTIC-PLANE BAND ("you are inside a galaxy") =====================
// A bright warm band of dense gas + stars along a tilted great circle, like the
// Milky Way arching across the sky. planeN = the pole of the galactic plane.
float3 planeN = normalize(float3(0.18, 0.30, 1.0));
float distToPlane = abs(dot(dir, planeN));          // 0 on the band, 1 at the poles
float band = exp(-distToPlane * distToPlane * 90.0);          // tighter bright core
float bandWide = exp(-distToPlane * distToPlane * 16.0) * 0.35; // softer, narrower halo
// Break the band with the fbm so it's a textured arch, not a clean wash
float bandMask = (band + bandWide) * (0.4 + 0.8 * fbm);
float3 bandColor = float3(1.0, 0.82, 0.55);          // warm galactic glow
col += bandColor * bandMask * 0.05;   // faint galactic arch, not a white stripe

// ===================== STARS =====================
// Dense star concentration along the galactic band (the Milky Way star clouds)
{
    float bandStarScale = 320.0;
    float3 bcell = floor(dir * bandStarScale);
    float bh = HASH3(bcell + 5.0);
    float bandStarThresh = lerp(0.9995, 0.985, saturate(band)); // subtle band density
    if (bh > bandStarThresh)
    {
        float bh2 = frac(sin(bh * 51.0 + 3.0) * 22441.7);
        float3 bjit = (float3(bh, bh2, frac(bh + bh2)) - 0.5);
        float3 bc = normalize((bcell + 0.5 + bjit * 0.5) / bandStarScale);
        float ad = acos(saturate(dot(dir, bc)));
        col += exp(-ad * ad / (0.0004 * 0.0004)) * float3(1.0, 0.92, 0.8) * 1.2;
    }
}
[unroll]
for (int oct = 0; oct < 2; oct++)
{
    float scale = (oct == 0) ? 90.0 : 220.0;
    float threshold = (oct == 0) ? 0.992 : 0.9975;
    float starRadius = (oct == 0) ? 0.0007 : 0.00035;
    float3 cell = floor(dir * scale);
    float h = HASH3(cell);
    if (h > threshold)
    {
        float h2 = frac(sin(h * 78.233 + 1.0) * 51123.43);
        float h3 = frac(sin(h * 41.5 + 2.0) * 99117.91);
        float3 jitter = float3(h2, h3, frac(h2 + h3)) - 0.5;
        float3 starCenter = normalize((cell + 0.5 + jitter * 0.4) / scale);
        float angDist = acos(saturate(dot(dir, starCenter)));
        float bright = exp(-angDist * angDist / (starRadius * starRadius));
        float t = frac(h * 17.0);
        float3 tint = lerp(float3(1.0, 0.85, 0.7), float3(0.75, 0.85, 1.0), t);
        float mag = lerp(0.4, 3.0, frac(h * 7.13));
        col += bright * tint * mag;
    }
}

return col;
""")

# The custom node needs an input named "ViewDir"
custom_input = unreal.CustomInput()
custom_input.set_editor_property('input_name', 'ViewDir')
star_node.set_editor_property('inputs', [custom_input])

# ---------- Feed ViewDir = WorldPosition - CameraPosition (normalized) ----------
world_pos = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -900, -100)
cam_pos  = mel.create_material_expression(mat, unreal.MaterialExpressionCameraPositionWS, -900, 100)
subtract = mel.create_material_expression(mat, unreal.MaterialExpressionSubtract, -700, 0)
normalize = mel.create_material_expression(mat, unreal.MaterialExpressionNormalize, -550, 0)

mel.connect_material_expressions(world_pos, '', subtract, 'A')
mel.connect_material_expressions(cam_pos,   '', subtract, 'B')
mel.connect_material_expressions(subtract,  '', normalize, '')
mel.connect_material_expressions(normalize, '', star_node, 'ViewDir')

# ---------- DomeBrightness knob (live) -> Emissive ----------
# Lets us dial the whole background dark (Interstellar look) without a rebuild.
dome_bri = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -200, 250)
dome_bri.set_editor_property('parameter_name', 'DomeBrightness')
dome_bri.set_editor_property('default_value', 0.15)
dome_mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -150, 0)
mel.connect_material_expressions(star_node, '', dome_mul, 'A')
mel.connect_material_expressions(dome_bri, '', dome_mul, 'B')
mel.connect_material_property(dome_mul, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created and compiled: {FULL_PATH}')
