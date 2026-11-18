import unreal
ar=unreal.AssetRegistryHelpers.get_asset_registry()
deps=ar.get_dependencies(unreal.Name('/Game/AlienSkies/Materials/M_PPLensing'),
                         unreal.AssetRegistryDependencyOptions(include_hard_package_references=True))
print('M_PPLensing dependencies:')
mpc_dep=False
for d in deps:
    s=str(d)
    print('  ',s)
    if 'MPC_BlackHole' in s: mpc_dep=True
print('=> MPC-driven (reads MPC_BlackHole):', mpc_dep)
print('=> (if False, it is the BAKED-literal version, stuck at one pose)')
