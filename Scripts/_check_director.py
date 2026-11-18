import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
found=[]
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    l=a.get_actor_label()
    if 'SceneDirector' in cn or 'SceneDirector' in l or 'Director' in l:
        found.append((l,cn))
        # check MPC assignment
        try:
            mpc=a.get_editor_property('MPC_BlackHole')
            print(f'  {l} ({cn}) MPC_BlackHole={mpc}')
        except Exception as e:
            print(f'  {l} ({cn}) - no MPC prop: {e}')
print('SceneDirector actors:', found if found else 'NONE PLACED')
