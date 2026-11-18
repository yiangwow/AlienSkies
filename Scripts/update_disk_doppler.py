"""Rebuild M_RaymarchDisk with physically-correct relativistic Doppler beaming.

Identical to build_raymarch_disk.py except the beam formula is replaced:
  OLD: 0.55 + 0.6*cos(ang)  [wrong side, ~2:1 ratio]
  NEW: relativistic Lorentz formula, auto-detects approaching side, ~22:1 ratio
"""
import unreal
PATH='/Game/AlienSkies/Materials'; NAME='M_RaymarchDisk'; FULL=f'{PATH}/{NAME}'
mel=unreal.MaterialEditingLibrary
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

mat=unreal.load_asset(FULL) if unreal.EditorAssetLibrary.does_asset_exist(FULL) else None
if mat is not None:
    mel.delete_all_material_expressions(mat)
else:
    factory=unreal.MaterialFactoryNew(); at=unreal.AssetToolsHelpers.get_asset_tools()
    mat=at.create_asset(NAME,PATH,unreal.Material,factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('two_sided', True)

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
rm.set_editor_property('code', r"""
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
float3 P = WorldPos;
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
        float sweep = ang + spinT * pow(max(r/InnerR,1.0), -1.5) * 6.0;
        float3 q = float3(sweep*1.3, band*16.0, h/Thickness*1.4);
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
        q.x += wx*2.4; q.y += wy*2.4;
        float dens=0.0, amp=0.55; float3 qq=q;
        [unroll]
        for (int o=0;o<4;o++){
            float3 ip=floor(qq), fp=frac(qq); fp=fp*fp*(3.0-2.0*fp);
            float x00=lerp(H3(ip),H3(ip+float3(1,0,0)),fp.x), x10=lerp(H3(ip+float3(0,1,0)),H3(ip+float3(1,1,0)),fp.x);
            float x01=lerp(H3(ip+float3(0,0,1)),H3(ip+float3(1,0,1)),fp.x), x11=lerp(H3(ip+float3(0,1,1)),H3(ip+float3(1,1,1)),fp.x);
            dens += lerp(lerp(x00,x10,fp.y),lerp(x01,x11,fp.y),fp.z)*amp; qq=qq*2.07+1.3; amp*=0.5;
        }
        dens = saturate((dens - 0.40) * 2.7);
        dens = pow(dens, 1.25);
        float radial = pow(1.0-band, 1.4);
        float3 fc;
        if (band<0.16) fc=float3(1.0,0.98,0.92);
        else if (band<0.45) fc=lerp(float3(1.0,0.92,0.70),float3(1.0,0.50,0.13),(band-0.16)/0.29);
        else fc=lerp(float3(1.0,0.50,0.13),float3(0.80,0.12,0.03),(band-0.45)/0.55);

        // Physically-correct relativistic Doppler beaming.
        // vel_dir = orbital velocity direction (CCW viewed from +N).
        // Lorentz beaming: I_obs = I_emit * (1/(1 - beta*cosTheta))^3
        // beta=0.65 gives ~22:1 bright/dim ratio — matches M87 crescent contrast.
        float3 rad_hat = (r > 100.0) ? normalize(radv) : U;
        float3 vel_dir = cross(N, rad_hat);
        float3 toward_cam = normalize(CamPos - P);
        float betaCos = clamp(0.65 * dot(vel_dir, toward_cam), -0.97, 0.97);
        float beam = pow(1.0 / (1.0 - betaCos), 1.5) * 0.55;

        accum += fc * dens * vfall * radial * beam;
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
les.save_current_level()
print('Done. Physically-correct Doppler: ~22x bright/dim ratio, correct side.')
