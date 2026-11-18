"""M_Jet — relativistic jet for the black hole, WISPY/WARPY rework (TON 618 ref:
ton618-jet-from-planet.png — warpy flaring cone of fine turbulent filaments, not a
solid beam). Additive, unlit, two-sided. Domain-warped fbm streams up the jet so it
reads as flowing wisps with frayed soft edges; Time-animated.
"""
import unreal
PATH='/Game/AlienSkies/Materials'; NAME='M_Jet'; FULL=f'{PATH}/{NAME}'
mel=unreal.MaterialEditingLibrary
# rebuild in place so live jet MaterialInstanceDynamics keep their parent
if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    mat=unreal.load_asset(FULL); mel.delete_all_material_expressions(mat)
else:
    factory=unreal.MaterialFactoryNew(); at=unreal.AssetToolsHelpers.get_asset_tools()
    mat=at.create_asset(NAME,PATH,unreal.Material,factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)
uv=mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -900, 0)
tnode=mel.create_material_expression(mat, unreal.MaterialExpressionTime, -900, 200)
node=mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -550, 0)
node.set_editor_property('description','JetWisp')
node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
node.set_editor_property('code', """
#define H(p) frac(sin(dot(p, float2(127.1,311.7))) * 43758.5453)
// UV.y: 0 at core (base), 1 at tip. UV.x: around the cone (0..1).
float along  = UV.y;
float around = UV.x;
float t = Time * 0.22;

// Coords streaming UP the jet; domain-warp them so filaments curl/warp (not straight).
// All noise INLINE (HLSL forbids nested functions inside a Custom node).
float2 p = float2(around * 7.0, along * 5.5 - t);
float wxn, wyn;
{ float2 pa=p*0.6+1.3, ip=floor(pa), fp=frac(pa); fp=fp*fp*(3.0-2.0*fp);
  wxn=lerp(lerp(H(ip),H(ip+float2(1,0)),fp.x),lerp(H(ip+float2(0,1)),H(ip+float2(1,1)),fp.x),fp.y)-0.5; }
{ float2 pa=p*0.6+8.1, ip=floor(pa), fp=frac(pa); fp=fp*fp*(3.0-2.0*fp);
  wyn=lerp(lerp(H(ip),H(ip+float2(1,0)),fp.x),lerp(H(ip+float2(0,1)),H(ip+float2(1,1)),fp.x),fp.y)-0.5; }
p += float2(wxn, wyn) * 2.0;                 // warp -> curved wisps
float wisp=0.0, amp=0.5; float2 pp=p;
[unroll]
for(int i=0;i<5;i++){
  float2 ip=floor(pp), fp=frac(pp); fp=fp*fp*(3.0-2.0*fp);
  wisp += lerp(lerp(H(ip),H(ip+float2(1,0)),fp.x),lerp(H(ip+float2(0,1)),H(ip+float2(1,1)),fp.x),fp.y)*amp;
  pp=pp*2.03+1.7; amp*=0.5;
}
wisp = pow(saturate(wisp * 1.25), 1.7);      // crisp filament streaks + dark gaps

// Width profile across the cone: soft center; wisps fray the edges.
float rad = 1.0 - abs(frac(around) - 0.5) * 2.0;   // 1 center, 0 seam
rad = smoothstep(0.0, 0.55, rad);
float edge = smoothstep(0.15, 0.75, rad + (wisp - 0.5) * 0.6);

// Length: blazing at the core, long wispy fade toward the tip.
float lf = pow(saturate(1.0 - along), 0.5);
float core = exp(-along * along * 22.0) * 1.2;     // hot base knot

float dens = edge * lf * (0.20 + 1.5 * wisp) + core * edge;

// Warm-white hot base -> cooler bluish tip (subtle).
float3 hot = float3(1.0, 0.95, 0.86);
float3 tip = float3(0.70, 0.82, 1.0);
float3 col = lerp(hot, tip, along);
return col * dens;
""")
ci=unreal.CustomInput(); ci.set_editor_property('input_name','UV')
ti=unreal.CustomInput(); ti.set_editor_property('input_name','Time')
node.set_editor_property('inputs',[ci,ti])
mel.connect_material_expressions(uv,'',node,'UV')
mel.connect_material_expressions(tnode,'',node,'Time')
b=mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -550, 230)
b.set_editor_property('parameter_name','Brightness'); b.set_editor_property('default_value',9.0)
mul=mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -220, 60)
mel.connect_material_expressions(node,'',mul,'A'); mel.connect_material_expressions(b,'',mul,'B')
mel.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL} (wispy)')
