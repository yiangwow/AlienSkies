"""M_Lensing — gravitational lensing for the black hole.
A translucent sphere (larger than the hole) that REFRACTS the background (bends
stars/disk around it, strongest at the silhouette) + a bright Einstein ring at the
rim. This is the localized real-time lensing approximation (works from any angle,
no screen-position plumbing). Spawns the lensing sphere on the existing black hole.
"""
import unreal, math
PATH='/Game/AlienSkies/Materials'; NAME='M_Lensing'; FULL=f'{PATH}/{NAME}'
if unreal.EditorAssetLibrary.does_asset_exist(FULL):
    unreal.EditorAssetLibrary.delete_asset(FULL)
factory=unreal.MaterialFactoryNew(); at=unreal.AssetToolsHelpers.get_asset_tools()
mat=at.create_asset(NAME,PATH,unreal.Material,factory)
mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property('two_sided', True)
mel=unreal.MaterialEditingLibrary

fres=mel.create_material_expression(mat,unreal.MaterialExpressionFresnel,-700,0)
fres.set_editor_property('exponent',4.0); fres.set_editor_property('base_reflect_fraction',0.0)

# Einstein ring: sharp fresnel^k glow at the rim
ringpow=mel.create_material_expression(mat,unreal.MaterialExpressionPower,-480,-120)
mel.connect_material_expressions(fres,'',ringpow,'Base')
pe=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-620,-60); pe.set_editor_property('r',7.0)
mel.connect_material_expressions(pe,'',ringpow,'Exp')
ringcol=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-480,-200)
ringcol.set_editor_property('constant',unreal.LinearColor(1.0,0.8,0.5,1.0))
ringmul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-280,-150)
mel.connect_material_expressions(ringpow,'',ringmul,'A'); mel.connect_material_expressions(ringcol,'',ringmul,'B')
ringbri=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-120,-150)
rb=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-280,-40); rb.set_editor_property('r',7.0)
mel.connect_material_expressions(ringmul,'',ringbri,'A'); mel.connect_material_expressions(rb,'',ringbri,'B')
mel.connect_material_property(ringbri,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)

# Opacity: faint, denser at rim (so the ring shows + a little body)
op=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-280,120)
opf=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-480,160); opf.set_editor_property('r',0.85)
mel.connect_material_expressions(fres,'',op,'A'); mel.connect_material_expressions(opf,'',op,'B')
mel.connect_material_property(op,'',unreal.MaterialProperty.MP_OPACITY)

# Refraction: bend background; IOR ~1 center -> ~1.5 at silhouette
ior=mel.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate,-280,260)
i1=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-480,240); i1.set_editor_property('r',1.0)
i2=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-480,300); i2.set_editor_property('r',1.55)
mel.connect_material_expressions(i1,'',ior,'A'); mel.connect_material_expressions(i2,'',ior,'B')
mel.connect_material_expressions(fres,'',ior,'Alpha')
mel.connect_material_property(ior,'',unreal.MaterialProperty.MP_REFRACTION)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Created {FULL}')

# ---- spawn the lensing sphere on the black hole ----
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sphere=unreal.load_asset('/Engine/BasicShapes/Sphere')
CENTER=unreal.Vector(-620000,0,230000); HOLE_R=13000.0
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='BlackHole_Lensing': eas.destroy_actor(a)
a=eas.spawn_actor_from_class(unreal.StaticMeshActor, CENTER, unreal.Rotator(0,0,0))
a.set_actor_label('BlackHole_Lensing'); a.set_editor_property('is_spatially_loaded',False)
smc=a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_editor_property('static_mesh',sphere); smc.set_mobility(unreal.ComponentMobility.MOVABLE)
smc.set_editor_property('cast_shadow',False)
ls=(HOLE_R*2.3)/50.0
a.set_actor_scale3d(unreal.Vector(ls,ls,ls))
smc.set_material(0,mat)
les.save_current_level()
print('Lensing sphere spawned')
