import unreal

print("Creating Input Actions using asset tools...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# Create the actual objects
ia_look = unreal.new_object(unreal.InputAction)
ia_zoom = unreal.new_object(unreal.InputAction)
imc = unreal.new_object(unreal.InputMappingContext)

# Save them using the asset tools
asset_tools.create_asset("IA_Look", "/Game/AlienSkies/DataAssets/", ia_look)
print("Created IA_Look")

asset_tools.create_asset("IA_Zoom", "/Game/AlienSkies/DataAssets/", ia_zoom)
print("Created IA_Zoom")

asset_tools.create_asset("IMC_AlienSkies", "/Game/AlienSkies/DataAssets/", imc)
print("Created IMC_AlienSkies")

print("Done! All input assets created.")
