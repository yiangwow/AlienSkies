"""M_MechHybrid (UNLIT - the scene has no lights, like the galaxy/black hole/stardome, so a lit
material would render black). Emissive = lerp(BaseColor, AccentColor*AccentGlow*flicker, vcol.R)
plus a Fresnel rim so the dark body still reads as 3D form. Subtle WPO sway for idle life.
Tunable scalars: AccentGlow, FlickerAmp, SwayAmp, SwaySpeed, RimGlow."""
import unreal
PATH = '/Game/AlienSkies/Materials'; NAME = 'M_MechHybrid'; FULL = f'{PATH}/{NAME}'
mel = unreal.MaterialEditingLibrary

mat = unreal.load_asset(FULL) if unreal.EditorAssetLibrary.does_asset_exist(FULL) else None
if mat is not None:
    mel.delete_all_material_expressions(mat)
else:
    factory = unreal.MaterialFactoryNew(); at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(NAME, PATH, unreal.Material, factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)


def sc(name, val, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1400, y)
    n.set_editor_property('parameter_name', name); n.set_editor_property('default_value', float(val))
    return n


def vec(name, col, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -1400, y)
    n.set_editor_property('parameter_name', name); n.set_editor_property('default_value', col)
    return n


def const(v, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -1100, y)
    n.set_editor_property('r', float(v)); return n


p_glow = sc('AccentGlow', 5.0, -300); p_fa = sc('FlickerAmp', 0.30, -240)
p_sa = sc('SwayAmp', 1.5, -180); p_ss = sc('SwaySpeed', 1.1, -120); p_rim = sc('RimGlow', 0.5, -60)
c_accent = vec('AccentColor', unreal.LinearColor(0.10, 0.70, 1.20, 1.0), 40)
c_base = vec('BaseColor', unreal.LinearColor(0.05, 0.055, 0.07, 1.0), 120)
c_rim = vec('RimColor', unreal.LinearColor(0.20, 0.45, 0.80, 1.0), 200)

tnode = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -1100, 360)
vcol = mel.create_material_expression(mat, unreal.MaterialExpressionVertexColor, -1100, 440)
fres = mel.create_material_expression(mat, unreal.MaterialExpressionFresnel, -1100, 520)

# flicker = 1 + FlickerAmp * sin(Time*8)
mul8 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -900, 360)
mel.connect_material_expressions(tnode, '', mul8, 'A'); mel.connect_material_expressions(const(8.0, 400), '', mul8, 'B')
sin8 = mel.create_material_expression(mat, unreal.MaterialExpressionSine, -760, 360)
mel.connect_material_expressions(mul8, '', sin8, '')
fm = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -620, 360)
mel.connect_material_expressions(sin8, '', fm, 'A'); mel.connect_material_expressions(p_fa, '', fm, 'B')
flick = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -480, 360)
mel.connect_material_expressions(fm, '', flick, 'A'); mel.connect_material_expressions(const(1.0, 400), '', flick, 'B')

# accent_emissive = AccentColor * AccentGlow * flicker
a1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -620, 40)
mel.connect_material_expressions(c_accent, '', a1, 'A'); mel.connect_material_expressions(p_glow, '', a1, 'B')
a2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -480, 40)
mel.connect_material_expressions(a1, '', a2, 'A'); mel.connect_material_expressions(flick, '', a2, 'B')

# rim = Fresnel * RimGlow * RimColor  -> added to base so the dark body shows silhouette form
r1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -760, 520)
mel.connect_material_expressions(fres, '', r1, 'A'); mel.connect_material_expressions(p_rim, '', r1, 'B')
r2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -620, 520)
mel.connect_material_expressions(r1, '', r2, 'A'); mel.connect_material_expressions(c_rim, '', r2, 'B')
base_plus_rim = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -480, 200)
mel.connect_material_expressions(c_base, '', base_plus_rim, 'A'); mel.connect_material_expressions(r2, '', base_plus_rim, 'B')

# emissive = lerp(base+rim, accent, vcol.R)
lerp = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -300, 200)
mel.connect_material_expressions(base_plus_rim, '', lerp, 'A')
mel.connect_material_expressions(a2, '', lerp, 'B')
mel.connect_material_expressions(vcol, 'R', lerp, 'Alpha')
mel.connect_material_property(lerp, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

# WPO idle sway: world offset (sx, 0, sz), sx/sz = SwayAmp*sin(Time*SwaySpeed*{1,0.7})
def sway(freqmul, ampmul, y):
    f1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -900, y)
    mel.connect_material_expressions(tnode, '', f1, 'A'); mel.connect_material_expressions(p_ss, '', f1, 'B')
    f2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -780, y)
    mel.connect_material_expressions(f1, '', f2, 'A'); mel.connect_material_expressions(const(freqmul, y + 40), '', f2, 'B')
    s = mel.create_material_expression(mat, unreal.MaterialExpressionSine, -660, y)
    mel.connect_material_expressions(f2, '', s, '')
    m1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -540, y)
    mel.connect_material_expressions(s, '', m1, 'A'); mel.connect_material_expressions(p_sa, '', m1, 'B')
    m2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -420, y)
    mel.connect_material_expressions(m1, '', m2, 'A'); mel.connect_material_expressions(const(ampmul, y + 40), '', m2, 'B')
    return m2


sx = sway(1.0, 1.0, 640); sz = sway(0.7, 0.7, 780)
ap1 = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -280, 700)
mel.connect_material_expressions(sx, '', ap1, 'A'); mel.connect_material_expressions(const(0.0, 740), '', ap1, 'B')
wpo = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -160, 720)
mel.connect_material_expressions(ap1, '', wpo, 'A'); mel.connect_material_expressions(sz, '', wpo, 'B')
mel.connect_material_property(wpo, '', unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('M_MechHybrid (unlit) built.')
