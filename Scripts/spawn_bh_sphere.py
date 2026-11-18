"""Spawn (or update) the physical black-hole shadow sphere.

A flat-black opaque sphere mesh placed at the black hole's world position.
This provides proper 3D occlusion — the disk, stars, and planets are blocked
by real depth, which the post-process shadow can't do. The PP lensing then
bends background light around this sphere's silhouette.

The sphere's world radius matches BlackHoleRadius (13000 cm). UE's SM_Sphere
has radius 50 cm at scale 1, so scale = 13000 / 50 = 260.
"""
import unreal

BH_LOC  = unreal.Vector(-620000.0, 0.0, 230000.0)
BH_RADIUS = 13000.0          # cm, matches SceneDirector.h BlackHoleRadius
SPHERE_BASE_RADIUS = 50.0    # UE SM_Sphere radius at scale 1
SCALE = BH_RADIUS / SPHERE_BASE_RADIUS  # = 260

LABEL   = 'BlackHole_Shadow'
MAT_PATH = '/Game/AlienSkies/Materials'
MAT_NAME = 'M_BHShadow'
MAT_FULL = f'{MAT_PATH}/{MAT_NAME}'

# ---- 1. build a flat black unlit opaque material (idempotent) ----
mel = unreal.MaterialEditingLibrary
if unreal.EditorAssetLibrary.does_asset_exist(MAT_FULL):
    mat = unreal.load_asset(MAT_FULL)
    mel.delete_all_material_expressions(mat)
else:
    factory = unreal.MaterialFactoryNew()
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)

mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
mat.set_editor_property('two_sided', False)

black = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
black.set_editor_property('constant', unreal.LinearColor(0.0, 0.0, 0.0, 1.0))
mel.connect_material_property(black, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
print(f'Built {MAT_FULL}')

# ---- 2. find or spawn the shadow sphere actor ----
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

existing = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == LABEL:
        existing = a
        break

sphere_mesh = unreal.load_asset('/Engine/BasicShapes/Sphere')

if existing:
    actor = existing
    print(f'Found existing {LABEL}, updating.')
else:
    actor = eas.spawn_actor_from_class(
        unreal.StaticMeshActor,
        BH_LOC,
        unreal.Rotator(0, 0, 0)
    )
    actor.set_actor_label(LABEL)
    print(f'Spawned new {LABEL}')

actor.set_actor_location(BH_LOC, False, False)
actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))

smc = actor.static_mesh_component
smc.set_static_mesh(sphere_mesh)
smc.set_material(0, mat)

# Don't cast shadows — it's a void sphere in space, no light source to cast from
smc.set_editor_property('cast_shadow', False)

les.save_current_level()
print(f'{LABEL} placed at {BH_LOC}, scale={SCALE} (radius={BH_RADIUS}cm)')
