import unreal
cands=[c for c in dir(unreal) if 'Material' in c and ('Kismet' in c or 'Collection' in c or 'Parameter' in c)]
print("classes:",cands)
for c in cands:
    cls=getattr(unreal,c)
    fns=[f for f in dir(cls) if 'scalar' in f.lower() or 'vector' in f.lower() or 'collection' in f.lower()]
    if fns: print(c,"->",fns)
# world method?
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); w=ues.get_editor_world()
print("World has get_parameter_collection_instance:", hasattr(w,'get_parameter_collection_instance'))
