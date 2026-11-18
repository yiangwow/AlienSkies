import unreal

lib = unreal.EditorAssetLibrary()

# Create MPC_TimeOfDay (since MPC_BlackHole already exists, just create the second one)
print("Creating MPC_TimeOfDay...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.MaterialParameterCollectionFactoryNew()

mpc_tod = asset_tools.create_asset("MPC_TimeOfDay", "/Game/AlienSkies/DataAssets/", unreal.MaterialParameterCollection, factory)
lib.save_asset("/Game/AlienSkies/DataAssets/MPC_TimeOfDay")

print("MPC_TimeOfDay created!")
print("Done! Now open both MPCs in the editor and manually add the parameters listed in WEEK1-IMPLEMENTATION-GUIDE.md")
