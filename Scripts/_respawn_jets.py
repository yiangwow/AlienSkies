"""Respawn jets as thin wispy beams (safe orientation: original spawn_blackhole style).
Flaring-cone shape is a later polish; this restores a clean wispy relativistic beam."""
import unreal, math
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ml=unreal.MathLibrary
cone=unreal.load_asset('/Engine/BasicShapes/Cone')
m_jet=unreal.load_asset('/Game/AlienSkies/Materials/M_Jet')
CENTER=unreal.Vector(-620000,0,230000)
to_cam=(1.0,0.0,0.10); _l=math.sqrt(sum(c*c for c in to_cam)); to_cam=tuple(c/_l for c in to_cam)
ax=(to_cam[1],-to_cam[0],0.0); _al=math.sqrt(sum(c*c for c in ax)) or 1.0; ax=tuple(c/_al for c in ax)
N=ml.rotate_angle_axis(unreal.Vector(*to_cam),52.0,unreal.Vector(*ax))
JET_LEN=560.0; half=50.0*JET_LEN
for a in eas.get_all_level_actors():
    if a.get_actor_label() in ('BlackHole_JetN','BlackHole_JetS','BlackHole_JetSheathN','BlackHole_JetSheathS'):
        eas.destroy_actor(a)
def spawn(label, scale, rot, pos, br):
    act=eas.spawn_actor_from_class(unreal.StaticMeshActor, pos, rot)
    act.set_actor_label(label); act.set_editor_property('is_spatially_loaded',False)
    smc=act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_editor_property('static_mesh',cone); smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_editor_property('cast_shadow',False)
    act.set_actor_scale3d(scale)
    mid=smc.create_dynamic_material_instance(0,m_jet); mid.set_scalar_parameter_value('Brightness',br)
for sgn,tag in ((1.0,'N'),(-1.0,'S')):
    axis=unreal.Vector(N.x*sgn,N.y*sgn,N.z*sgn); rot=ml.make_rot_from_z(axis)
    pos=unreal.Vector(CENTER.x+axis.x*half, CENTER.y+axis.y*half, CENTER.z+axis.z*half)
    spawn(f'BlackHole_Jet{tag}', unreal.Vector(13.0,13.0,JET_LEN), rot, pos, 24.0)
    spawn(f'BlackHole_JetSheath{tag}', unreal.Vector(34.0,34.0,JET_LEN*0.9), rot, pos, 6.0)
    print('jet',tag,'respawned (thin wispy beam)')
les.save_current_level()
