"""Spawn the FP mech viewmodel: one StaticMeshActor per part (claw, weapon, struts), each
attached to the camera pawn's CameraComponent in FP-local space. Re-runnable (destroys prior
'MechViewmodel*' actors). Saves the level.

Orientation: the imported mesh's drill points along mesh-local -Y; yaw +90 maps that to the
camera's local +X (forward). Tune RIG_OFFSET / RIG_ROT / RIG_SCALE from the FP capture."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

MECH = '/Game/AlienSkies/Mech'
PART_NAMES = ['Mech_LeftClaw', 'Mech_RightWeapon', 'Mech_Struts']
RIG_OFFSET = unreal.Vector(0.0, 0.0, -10.0)     # cm: forward(+X), lateral(+Y), vertical(+Z)
RIG_ROT = unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0)  # yaw+90 -> arms extend forward INTO view
RIG_SCALE = 1.0

cam_pawn = cam_comp = None
for a in eas.get_all_level_actors():
    cc = a.get_component_by_class(unreal.CameraComponent)
    if cc:
        cam_pawn, cam_comp = a, cc
        break
if cam_comp is None:
    raise RuntimeError('No CameraComponent pawn found in level')

for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('MechViewmodel'):
        eas.destroy_actor(a)

m_mech = unreal.load_asset('/Game/AlienSkies/Materials/M_MechHybrid')  # None until Task 6
for name in PART_NAMES:
    mesh = unreal.load_asset(f'{MECH}/{name}')
    sma = eas.spawn_actor_from_class(unreal.StaticMeshActor, cam_pawn.get_actor_location())
    sma.set_actor_label(f'MechViewmodel_{name}')
    sma.set_editor_property('is_spatially_loaded', False)
    smc = sma.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_editor_property('static_mesh', mesh)
    smc.set_editor_property('cast_shadow', False)
    if m_mech:
        smc.set_material(0, m_mech)
    sma.attach_to_component(cam_comp, '',
                            unreal.AttachmentRule.KEEP_RELATIVE,
                            unreal.AttachmentRule.KEEP_RELATIVE,
                            unreal.AttachmentRule.KEEP_RELATIVE, False)
    sma.set_actor_relative_location(RIG_OFFSET, False, False)
    sma.set_actor_relative_rotation(RIG_ROT, False, False)
    sma.set_actor_relative_scale3d(unreal.Vector(RIG_SCALE, RIG_SCALE, RIG_SCALE))

les.editor_invalidate_viewports(); les.save_current_level()
print('MechViewmodel attached to', cam_pawn.get_actor_label(), 'parts=', PART_NAMES)
