"""Hot gas corona + infall streamers around the black hole.

Adds a large volumetric sphere (BlackHole_InfallCorona) that raymarchs through:
  - A hot equatorial plasma corona concentrated near the disk plane
  - Radially-elongated wispy filaments animated to flow inward over time

Together these give the sense of material being sucked in from 3D space and the
glowing environment that makes the hole feel embedded in something real.

Scale: ~5x the disk outer radius, so it's significantly larger than the disk.
"""
import unreal, math

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mel = unreal.MaterialEditingLibrary

CENTER = unreal.Vector(-620000, 0, 230000)
HOLE_R  = 13000.0
OUTER_R = HOLE_R * 6.0          # disk outer radius (~78000)
# HALO, not fog tank. The corona used to be 390000 (5x disk): the camera flies at 60k-160k so
# it was ALWAYS deep inside an additive volume -> golden fog filling the screen, hiding the
# background galaxies/stars, and lurching ('snap to black') as you moved through it.
# ~1.4x the disk: reads as a glowing envelope you can see from outside, with the cosmos beyond.
CORONA_R = 170000.0
INNER_R  = 16000.0              # hug the hole: haze starts just outside the photon ring (~14040)

# ---- remove old corona ----
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_InfallCorona':
        eas.destroy_actor(a)

# ---- build M_InfallCorona material ----
MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_InfallCorona'
FULL = f'{MAT_PATH}/{MAT_NAME}'

if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    mat = unreal.load_asset(FULL)
    mel.delete_all_material_expressions(mat)
else:
    factory = unreal.MaterialFactoryNew()
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)

mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)

def sc(name, val, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1300, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', float(val))
    return n

def vec(name, col, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -1300, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', col)
    return n

p_sphereR   = sc('SphereR',    CORONA_R,   -320)
p_innerR    = sc('InnerR',     INNER_R,    -260)
p_bri       = sc('Brightness', 0.18,       -200)
p_infspeed  = sc('InfallSpeed', 0.12,      -140)
p_N         = vec('DiskN', unreal.LinearColor(0, 0, 1, 0), -80)
p_U         = vec('DiskU', unreal.LinearColor(1, 0, 0, 0),  20)
p_V         = vec('DiskV', unreal.LinearColor(0, 1, 0, 0), 120)

cam   = mel.create_material_expression(mat, unreal.MaterialExpressionCameraPositionWS, -1300, 220)
wpos  = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition,    -1300, 300)
opos  = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1300, 380)
tnode = mel.create_material_expression(mat, unreal.MaterialExpressionTime,             -1300, 460)

hlsl = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -650, 100)
hlsl.set_editor_property('description', 'InfallCorona')
hlsl.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
hlsl.set_editor_property('code', """
#define H3(p) frac(sin(dot(p, float3(127.1,311.7,74.7)))*43758.5453)

float3 ro  = CamPos;
float3 rd  = normalize(WorldPos - ro);
float3 C   = Center;
float3 diskN = normalize(DiskN);
float3 diskU = normalize(DiskU);
float3 diskV = normalize(DiskV);

int STEPS = 56;
// Analytic ray-sphere intersection: march only the segment of the view ray that lies
// inside the corona sphere. tNear is clamped to 0 so this ALSO works when the camera is
// INSIDE the sphere — otherwise the rasterized WorldPos is the far interior wall, the
// march starts there and immediately exits (r>SphereR), and the haze vanishes up close.
float3 oc = ro - C;
float bq = dot(oc, rd);
float cq = dot(oc, oc) - SphereR * SphereR;
float disc = bq*bq - cq;
float3 accum = float3(0, 0, 0);
float stepLen = 0.0;
if (disc > 0.0) {
float sq = sqrt(disc);
float tNear = max(-bq - sq, 0.0);
float tFar  = -bq + sq;
stepLen = (tFar - tNear) / STEPS;
float3 P = ro + rd * (tNear + stepLen * 0.5);
float spinT = Time * InfallSpeed;
[loop]
for (int s = 0; s < STEPS; s++) {
    float3 rel = P - C;
    float r = length(rel);

    if (r < SphereR && r > InnerR) {
        float t  = r / SphereR;           // 0 = BH center, 1 = sphere edge
        float3 rhat = rel / r;

        // Decompose into disk-plane components
        float h = dot(rhat, diskN);        // -1..1, 0 = equatorial plane
        float3 rhat_eq = rhat - h * diskN;
        float req_len = length(rhat_eq);
        float3 rhat_eq_n = (req_len > 1e-4) ? rhat_eq / req_len : diskU;

        // Azimuth in disk plane (drives infall animation)
        float phi = atan2(dot(rhat_eq_n, diskV), dot(rhat_eq_n, diskU));

        // ---- infall wisp noise ----
        // High angular frequency + low radial: thin filaments stretched toward center.
        // phi + spinT makes them rotate/flow inward over time.
        float3 q = float3(phi * 1.8 + spinT, t * 10.0, h * 5.0);

        // 1-octave domain warp (elongates wisps radially)
        {
            float3 qa = q * 0.4 + 2.7;
            float3 ip = floor(qa), fp = frac(qa); fp = fp*fp*(3.-2.*fp);
            float wx = lerp(lerp(lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x),
                                lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x),fp.y),
                           lerp(lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x),
                                lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x),fp.y),fp.z);
            q.y += (wx - 0.5) * 2.5;   // stretch along radial
        }

        // 3-octave fbm for wispy density
        float dens = 0.0; float amp = 0.55; float3 qq = q;
        [unroll]
        for (int o = 0; o < 3; o++) {
            float3 ip = floor(qq), fp = frac(qq); fp = fp*fp*(3.-2.*fp);
            float d = lerp(lerp(lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x),
                               lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x),fp.y),
                          lerp(lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x),
                               lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x),fp.y),fp.z);
            dens += d * amp; qq = qq * 2.05 + 1.7; amp *= 0.5;
        }
        dens = saturate((dens - 0.40) * 3.2);
        dens = pow(dens, 1.4);

        // ---- radial + equatorial density shaping (HALO, not fog) ----
        // u: 0 at InnerR (hugging the hole) -> 1 at the sphere edge. Concentrate the glow
        // near the hole and fade smoothly to ZERO before the mesh boundary, so (a) the
        // background galaxies/stars show through the transparent outer haze and (b) there is
        // no hard sphere-edge pop. This is what turns the corona from a fog tank into an envelope.
        float u = saturate((r - InnerR) / (SphereR - InnerR));
        float radial     = pow(1.0 - u, 2.6);              // tight glow near the hole
        radial          *= smoothstep(1.0, 0.82, u);       // guarantee 0 at the boundary
        float equatorial = exp(-h * h * 5.0);              // disk-plane emphasis (softened)
        float density = dens * radial * (0.40 + 0.60 * equatorial);

        // ---- temperature gradient ----
        // Inner hot → outer dim; approaching hotter (tie to phi for subtle asymmetry)
        float3 fc_in  = float3(1.0, 0.60, 0.18);   // hot orange near center
        float3 fc_out = float3(0.55, 0.08, 0.01);  // dim red at edge
        float3 fc = lerp(fc_out, fc_in, pow(1.0 - u, 1.4));

        // Faint Doppler tint (so it echoes the disk's bright side)
        float dopp = 0.7 + 0.3 * cos(phi);
        fc *= dopp;

        accum += fc * density;
    }
    P += rd * stepLen;
}
}

return accum * (stepLen * 0.00020 * Brightness);
""")

for nm in ('CamPos','WorldPos','Center','DiskN','DiskU','DiskV',
           'SphereR','InnerR','Brightness','InfallSpeed','Time'):
    ci = unreal.CustomInput()
    ci.set_editor_property('input_name', nm)
    hlsl.set_editor_property('inputs', list(hlsl.get_editor_property('inputs')) + [ci])

mel.connect_material_expressions(cam,   '', hlsl, 'CamPos')
mel.connect_material_expressions(wpos,  '', hlsl, 'WorldPos')
mel.connect_material_expressions(opos,  '', hlsl, 'Center')
mel.connect_material_expressions(p_N,   '', hlsl, 'DiskN')
mel.connect_material_expressions(p_U,   '', hlsl, 'DiskU')
mel.connect_material_expressions(p_V,   '', hlsl, 'DiskV')
mel.connect_material_expressions(p_sphereR,  '', hlsl, 'SphereR')
mel.connect_material_expressions(p_innerR,   '', hlsl, 'InnerR')
mel.connect_material_expressions(p_bri,      '', hlsl, 'Brightness')
mel.connect_material_expressions(p_infspeed, '', hlsl, 'InfallSpeed')
mel.connect_material_expressions(tnode,      '', hlsl, 'Time')
mel.connect_material_property(hlsl, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'M_InfallCorona built.')

# ---- spawn the sphere actor ----
sphere_mesh = unreal.load_asset('/Engine/BasicShapes/Sphere')
a = eas.spawn_actor_from_class(unreal.StaticMeshActor, CENTER, unreal.Rotator(0, 0, 0))
a.set_actor_label('BlackHole_InfallCorona')
a.set_editor_property('is_spatially_loaded', False)
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_editor_property('static_mesh', sphere_mesh)
smc.set_mobility(unreal.ComponentMobility.MOVABLE)
smc.set_editor_property('cast_shadow', False)
# Sphere base radius is 50 units; scale so radius = CORONA_R cm
scale = CORONA_R / 50.0
a.set_actor_scale3d(unreal.Vector(scale, scale, scale))

# Set disk basis on the material — match spawn_rmdisk.py's disk_normal
import math
to_cam = (1.0, 0.0, 0.10)
_l = math.sqrt(sum(c*c for c in to_cam)); to_cam = tuple(c/_l for c in to_cam)
ax = (to_cam[1], -to_cam[0], 0.0); _al = math.sqrt(sum(c*c for c in ax)) or 1.0; ax = tuple(c/_al for c in ax)
ml = unreal.MathLibrary
N = ml.rotate_angle_axis(unreal.Vector(*to_cam), 52.0, unreal.Vector(*ax))
upref = unreal.Vector(0, 0, 1)
if abs(N.z) > 0.9: upref = unreal.Vector(1, 0, 0)
def cross(a, b): return unreal.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
def norm(v):
    L = math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z) or 1.0; return unreal.Vector(v.x/L, v.y/L, v.z/L)
U = norm(cross(upref, N)); V = norm(cross(N, U))

mid = smc.create_dynamic_material_instance(0, mat)
mid.set_scalar_parameter_value('SphereR',    CORONA_R)
mid.set_scalar_parameter_value('InnerR',     INNER_R)
mid.set_scalar_parameter_value('Brightness', 0.18)
mid.set_scalar_parameter_value('InfallSpeed', 0.12)
mid.set_vector_parameter_value('DiskN', unreal.LinearColor(N.x, N.y, N.z, 0))
mid.set_vector_parameter_value('DiskU', unreal.LinearColor(U.x, U.y, U.z, 0))
mid.set_vector_parameter_value('DiskV', unreal.LinearColor(V.x, V.y, V.z, 0))

les.save_current_level()
print(f'BlackHole_InfallCorona spawned. Corona radius={CORONA_R:.0f} cm ({CORONA_R/100:.0f} m).')
