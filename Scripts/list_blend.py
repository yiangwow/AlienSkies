import unreal
print([x for x in dir(unreal.BlendableLocation) if not x.startswith('_')])
