import unreal

print("Testing InputAction creation...")

# Try method 1: Using NewObject
try:
    ia_look = unreal.new_object(unreal.InputAction)
    print(f"Success: Created InputAction object: {ia_look}")
    print(f"Type: {type(ia_look)}")
except Exception as e:
    print(f"Failed: {e}")

# Check what methods are available on asset_tools
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
print(f"\nAvailable methods on asset_tools:")
methods = [m for m in dir(asset_tools) if not m.startswith('_')]
for method in methods[:10]:
    print(f"  - {method}")
