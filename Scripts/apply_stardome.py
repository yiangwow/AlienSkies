"""Apply M_StarDome to the existing SM_SkySphere actor in the level.
Also ensure it's large enough to enclose the play area and oriented so the
normals point inward (otherwise we'd see backfaces from inside).
"""
import unreal


def find_actor_by_label(label):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


sky_sphere = find_actor_by_label('SM_SkySphere')
if not sky_sphere:
    print('ERROR: no SM_SkySphere actor in level')
    raise SystemExit(1)

# Get the static mesh component
smc = sky_sphere.get_component_by_class(unreal.StaticMeshComponent)
if not smc:
    print('ERROR: SM_SkySphere has no StaticMeshComponent')
    raise SystemExit(1)

mesh = smc.get_editor_property('static_mesh')
print(f'Mesh: {mesh.get_path_name() if mesh else "None"}')
print(f'Materials before: {smc.get_num_materials()}')
for i in range(smc.get_num_materials()):
    m = smc.get_material(i)
    print(f'  [{i}] {m.get_path_name() if m else "None"}')

# Load and apply M_StarDome
star_mat = unreal.load_asset('/Game/AlienSkies/Materials/M_StarDome')
if not star_mat:
    print('ERROR: M_StarDome not found')
    raise SystemExit(1)

for i in range(smc.get_num_materials()):
    smc.set_material(i, star_mat)

# The default Engine SkySphere mesh is already inverted-normal so view from inside
# works without flipping. Scale it large to ensure we never clip out.
sky_sphere.set_actor_scale3d(unreal.Vector(400, 400, 400))
sky_sphere.set_actor_location(unreal.Vector(0, 0, 0), False, False)

sky_sphere.modify()
print('M_StarDome applied to SM_SkySphere, scale=400, location=(0,0,0)')

# Set initial StarBrightness via the MPC instance for the editor world
mpc = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.KismetMaterialLibrary.set_scalar_parameter_value(world, mpc, 'StarBrightness', 1.0)
print('MPC StarBrightness = 1.0')
