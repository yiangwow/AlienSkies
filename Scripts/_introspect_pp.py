import unreal
print("=== MaterialDomain ===")
print([m for m in dir(unreal.MaterialDomain) if not m.startswith('_')])
print("=== BlendableLocation ===")
print([m for m in dir(unreal.BlendableLocation) if not m.startswith('_')])
# does Material expose blendable_location / material_domain?
props = [p for p in dir(unreal.Material) if 'blend' in p.lower() or 'domain' in p.lower()]
print("=== Material props ===", props)
