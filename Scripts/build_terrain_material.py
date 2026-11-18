"""Create M_AlienTerrain — a simple dark rocky material driven by the
TerrainTintColor MPC param. Apply it to the Landscape actor.

Keeping it deliberately minimal for MVP:
- Base color: TerrainTintColor (MPC), darkened, with mild world-space noise
  to break up the flat look without textures
- Roughness: high (0.9)
- Normal: flat for now (will add Nanite displacement in Phase 4)
"""
import unreal

MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_AlienTerrain'
FULL_PATH = f'{MAT_PATH}/{MAT_NAME}'

if unreal.EditorAssetLibrary.does_asset_exist(FULL_PATH):
    print(f'Already exists: {FULL_PATH}')
else:
    factory = unreal.MaterialFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = asset_tools.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)

    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)

    mel = unreal.MaterialEditingLibrary

    # MPC: TerrainTintColor
    mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
    tint = mel.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, -700, 0)
    tint.set_editor_property('collection', mpc)
    tint.set_editor_property('parameter_name', 'TerrainTintColor')

    # Cheap noise variation: WorldPosition / 200 -> Noise -> 0..1
    world_pos = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -900, 200)
    divide = mel.create_material_expression(mat, unreal.MaterialExpressionDivide, -700, 200)
    divide.set_editor_property('const_b', 200.0)
    mel.connect_material_expressions(world_pos, '', divide, 'A')

    noise = mel.create_material_expression(mat, unreal.MaterialExpressionNoise, -500, 200)
    noise.set_editor_property('scale', 1.0)
    noise.set_editor_property('quality', 1)
    noise.set_editor_property('output_min', 0.4)
    noise.set_editor_property('output_max', 1.0)
    mel.connect_material_expressions(divide, '', noise, 'Position')

    # tint * noise -> base color
    mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, 100)
    mel.connect_material_expressions(tint, '', mul, 'A')
    mel.connect_material_expressions(noise, '', mul, 'B')

    mel.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)

    # Constant roughness
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 300)
    rough.set_editor_property('r', 0.9)
    mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)

    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    print(f'Created: {FULL_PATH}')


# ---------- Apply to all Landscape actors (main + streaming proxies) ----------
def find_actors_by_class(cls_name):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    return [a for a in eas.get_all_level_actors() if a.get_class().get_name() == cls_name]


alien_mat = unreal.load_asset(FULL_PATH)
landscapes = find_actors_by_class('Landscape') + find_actors_by_class('LandscapeStreamingProxy')
print(f'Found {len(landscapes)} landscape actors')
applied = 0
for ls in landscapes:
    try:
        ls.set_editor_property('landscape_material', alien_mat)
        ls.modify()
        applied += 1
    except Exception as e:
        print(f'  failed on {ls.get_actor_label()}: {e}')

print(f'Applied M_AlienTerrain to {applied}/{len(landscapes)} landscape actors')

# Set initial tint via MPC default — push it more reddish-brown
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
vps = list(mpc.get_editor_property('vector_parameters'))
for vp in vps:
    if str(vp.get_editor_property('parameter_name')) == 'TerrainTintColor':
        vp.set_editor_property('default_value', unreal.LinearColor(0.18, 0.07, 0.05, 1.0))
mpc.set_editor_property('vector_parameters', vps)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
print('TerrainTintColor default -> dark red-brown (0.18, 0.07, 0.05)')
