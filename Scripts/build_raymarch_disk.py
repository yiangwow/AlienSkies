"""M_RaymarchDisk — TRUE volumetric accretion disk via raymarching (the legit RT
technique). Applied to a Box mesh enclosing the disk. The pixel shader marches a
ray through a 3D turbulent density field shaped as a thin swirling torus, accumulates
fire-colored emission (white-hot inner -> orange -> red), with Keplerian swirl.

Params (set per-instance): DiskN/DiskU/DiskV (disk basis), InnerR, OuterR, Thickness,
Spin, Brightness. Center = ObjectPositionWS (box is centered on the hole).
"""
import unreal
PATH='/Game/AlienSkies/Materials'; NAME='M_RaymarchDisk'; FULL=f'{PATH}/{NAME}'
mel=unreal.MaterialEditingLibrary
# rebuild graph IN PLACE so the live MaterialInstanceDynamic on BlackHole_RMDisk keeps
# its parent (delete_asset would break it).
if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    mat=unreal.load_asset(FULL)
    mel.delete_all_material_expressions(mat)
else:
    factory=unreal.MaterialFactoryNew(); at=unreal.AssetToolsHelpers.get_asset_tools()
    mat=at.create_asset(NAME,PATH,unreal.Material,factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)
mel=unreal.MaterialEditingLibrary

def sc(name,val,y):
    n=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-1300,y)
    n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',float(val)); return n
def vec(name,col,y):
    n=mel.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,-1300,y)
    n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',col); return n

p_inner=sc('InnerR',20000.0,-260); p_outer=sc('OuterR',80000.0,-200)
p_thick=sc('Thickness',6000.0,-140); p_spin=sc('Spin',0.3,-80); p_bri=sc('Brightness',2.2,-20)
p_N=vec('DiskN',unreal.LinearColor(0,0,1,0),60); p_U=vec('DiskU',unreal.LinearColor(1,0,0,0),160)
p_V=vec('DiskV',unreal.LinearColor(0,1,0,0),260)

cam=mel.create_material_expression(mat,unreal.MaterialExpressionCameraPositionWS,-1300,360)
wpos=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-1300,440)
opos=mel.create_material_expression(mat,unreal.MaterialExpressionObjectPositionWS,-1300,520)
tnode=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-1300,600)

rm=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-650,100)
rm.set_editor_property('description','RaymarchDisk')
rm.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
rm.set_editor_property('code', """
#define H3(p) frac(sin(dot(p, float3(127.1,311.7,74.7)))*43758.5453)
float3 ro = CamPos;
float3 rd = normalize(WorldPos - ro);
float3 C = Center;
float3 N = normalize(DiskN);
float3 U = normalize(DiskU);
float3 V = normalize(DiskV);
int STEPS = 56;
float total = OuterR * 2.6;
float stepLen = total / STEPS;
float3 P = WorldPos;                 // start at the box front face
float3 accum = float3(0,0,0);
float spinT = Spin * Time;
[loop]
for (int s=0; s<STEPS; s++)
{
    float3 rel = P - C;
    float h = dot(rel, N);
    float3 radv = rel - h*N;
    float r = length(radv);
    if (r > InnerR && r < OuterR && abs(h) < Thickness*3.5)
    {
        float band = (r - InnerR)/(OuterR - InnerR);
        float vfall = exp(-(h*h)/(Thickness*Thickness));
        float u = dot(radv,U), v = dot(radv,V);
        float ang = atan2(v,u);
        // Keplerian swirl: inner rotates faster
        float sweep = ang + spinT * pow(max(r/InnerR,1.0), -1.5) * 6.0;
        // FINE wispy filaments: high radial freq streaked along the flow, domain-warped
        // so the gas curls into turbulent wisps (not a smooth band). All noise INLINE
        // (HLSL forbids nested functions inside a Custom node).
        float3 q = float3(sweep*1.3, band*16.0, h/Thickness*1.4);
        // -- domain warp: two single-octave value-noise samples (wx, wy) --
        float wx, wy;
        {
            float3 qa=q*0.5+1.7, ip=floor(qa), fp=frac(qa); fp=fp*fp*(3.0-2.0*fp);
            float x00=lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x), x10=lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x);
            float x01=lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x), x11=lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x);
            wx=lerp(lerp(x00,x10,fp.y),lerp(x01,x11,fp.y),fp.z)-0.5;
        }
        {
            float3 qa=q*0.5+8.3, ip=floor(qa), fp=frac(qa); fp=fp*fp*(3.0-2.0*fp);
            float x00=lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x), x10=lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x);
            float x01=lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x), x11=lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x);
            wy=lerp(lerp(x00,x10,fp.y),lerp(x01,x11,fp.y),fp.z)-0.5;
        }
        q.x += wx*2.4; q.y += wy*2.4;            // curl the filaments
        // -- 4-octave fbm (inline) for fine turbulent gas --
        float dens=0.0, amp=0.55; float3 qq=q;
        [unroll]
        for (int o=0;o<4;o++){
            float3 ip=floor(qq), fp=frac(qq); fp=fp*fp*(3.0-2.0*fp);
            float x00=lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x), x10=lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x);
            float x01=lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x), x11=lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x);
            dens += lerp(lerp(x00,x10,fp.y),lerp(x01,x11,fp.y),fp.z)*amp; qq=qq*2.07+1.3; amp*=0.5;
        }
        dens = saturate((dens - 0.40) * 2.7);      // crisp wisps + see-through gaps
        dens = pow(dens, 1.5);    // higher contrast -> sharper filaments, darker gaps
        float radial = pow(1.0-band, 1.4);
        float3 fc;
        if (band<0.16) fc=float3(1.0,0.98,0.92);
        else if (band<0.45) fc=lerp(float3(1.0,0.92,0.70),float3(1.0,0.50,0.13),(band-0.16)/0.29);
        else fc=lerp(float3(1.0,0.50,0.13),float3(0.80,0.12,0.03),(band-0.45)/0.55);
        // Relativistic Doppler beaming — power-law factor gives M87-style crescent.
        // Approaching side (cos(ang)=+1): ~6-7x brighter than receding (cos=-1).
        // Floor of 0.25 keeps receding side faintly visible (not pure black).
        float beam = 0.25 + 1.75 * pow(max(0.0, 0.5 + 0.5*cos(ang)), 2.5);
        // Chromatic Doppler tint: approaching = white-hot, receding = dim red
        float chroma = max(0.0, 0.5 + 0.5*cos(ang));
        float3 dtint = lerp(float3(0.88, 0.42, 0.10), float3(1.12, 1.04, 0.96), chroma);
        accum += fc * dtint * dens * vfall * radial * beam;
    }
    P += rd * stepLen;
}
return accum * (stepLen * 0.00020) * Brightness;
""")
for nm in ('CamPos','WorldPos','Center','DiskN','DiskU','DiskV','InnerR','OuterR','Thickness','Spin','Time','Brightness'):
    ci=unreal.CustomInput(); ci.set_editor_property('input_name',nm)
    rm.set_editor_property('inputs', list(rm.get_editor_property('inputs'))+[ci])
mel.connect_material_expressions(cam,'',rm,'CamPos')
mel.connect_material_expressions(wpos,'',rm,'WorldPos')
mel.connect_material_expressions(opos,'',rm,'Center')
mel.connect_material_expressions(p_N,'',rm,'DiskN')
mel.connect_material_expressions(p_U,'',rm,'DiskU')
mel.connect_material_expressions(p_V,'',rm,'DiskV')
mel.connect_material_expressions(p_inner,'',rm,'InnerR')
mel.connect_material_expressions(p_outer,'',rm,'OuterR')
mel.connect_material_expressions(p_thick,'',rm,'Thickness')
mel.connect_material_expressions(p_spin,'',rm,'Spin')
mel.connect_material_expressions(tnode,'',rm,'Time')
mel.connect_material_expressions(p_bri,'',rm,'Brightness')
mel.connect_material_property(rm,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL}')
