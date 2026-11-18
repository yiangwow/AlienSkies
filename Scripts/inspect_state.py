"""Print MPC parameter names and the actor inventory of the active level."""
import unreal

print('=' * 60)
print('MPC_TimeOfDay parameters:')
mpc_tod = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_TimeOfDay')
if mpc_tod:
    for sp in mpc_tod.get_editor_property('scalar_parameters'):
        print(f'  SCALAR  {sp.parameter_name} = {sp.default_value}')
    for vp in mpc_tod.get_editor_property('vector_parameters'):
        print(f'  VECTOR  {vp.parameter_name} = {vp.default_value}')
else:
    print('  NOT FOUND')

print()
print('MPC_BlackHole parameters:')
mpc_bh = unreal.load_asset('/Game/AlienSkies/DataAssets/MPC_BlackHole')
if mpc_bh:
    for sp in mpc_bh.get_editor_property('scalar_parameters'):
        print(f'  SCALAR  {sp.parameter_name} = {sp.default_value}')
    for vp in mpc_bh.get_editor_property('vector_parameters'):
        print(f'  VECTOR  {vp.parameter_name} = {vp.default_value}')
else:
    print('  NOT FOUND')

print()
print('=' * 60)
print('Active level actors:')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    label = a.get_actor_label()
    print(f'  {cls:30s}  "{label}"')
