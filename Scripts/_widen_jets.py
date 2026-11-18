"""Widen the jet cones so the wispy material reads as a flaring cone (not a thread),
and rebalance brightness. Editable knobs at top."""
import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
CORE_XY=34.0; SHEATH_XY=85.0; CORE_BR=16.0; SHEATH_BR=4.0
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l in ('BlackHole_JetN','BlackHole_JetS','BlackHole_JetSheathN','BlackHole_JetSheathS'):
        s=a.get_actor_scale3d()
        xy = SHEATH_XY if 'Sheath' in l else CORE_XY
        a.set_actor_scale3d(unreal.Vector(xy,xy,s.z))
        smc=a.get_component_by_class(unreal.StaticMeshComponent)
        mid=smc.get_material(0)
        if isinstance(mid,unreal.MaterialInstanceDynamic):
            mid.set_scalar_parameter_value('Brightness', SHEATH_BR if 'Sheath' in l else CORE_BR)
        print('adjusted',l,'xy',xy)
les.save_current_level()
