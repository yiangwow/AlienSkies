"""Re-assign M_StarDome to SM_SkySphere (it had reverted to DefaultMaterial -> missing background)."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MAT = '/Game/AlienSkies/Materials/M_StarDome'
mat = unreal.load_asset(MAT)
sky = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'SM_SkySphere':
        sky = a; break
if sky is None:
    print('SM_SkySphere NOT FOUND'); 
else:
    smc = sky.get_component_by_class(unreal.StaticMeshComponent)
    before = smc.get_material(0)
    smc.set_material(0, mat)
    after = smc.get_material(0)
    print('before =', before.get_name() if before else None)
    print('after  =', after.get_name() if after else None)
    les.save_current_level()
    print('Saved.')
