import unreal
print([f for f in dir(unreal.MaterialEditingLibrary) if 'express' in f.lower()])
