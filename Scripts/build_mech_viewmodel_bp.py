"""Bake the FP mech viewmodel INTO the BP_Camera Blueprint as StaticMeshComponents parented
under its CameraComponent. This makes the arms part of the possessed player pawn (visible in
editor AND Standalone, following the view) - unlike per-instance attachment, which doesn't stick.
Re-runnable: removes prior MechVM_* components first. Also clears the old stranded level actors."""
import unreal

BP_PATH = '/Game/AlienSkies/Blueprints/BP_Camera'
MECH = '/Game/AlienSkies/Mech'
PARTS = [('MechVM_Claw', 'Mech_LeftClaw'),
         ('MechVM_Weapon', 'Mech_RightWeapon'),
         ('MechVM_Struts', 'Mech_Struts')]
RIG_OFFSET = unreal.Vector(0.0, 0.0, -10.0)
RIG_ROT = unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0)
RIG_SCALE = 1.0

bp = unreal.load_asset(BP_PATH)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDBFL = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)


def obj_of(h):
    return SDBFL.get_object(SDBFL.get_data(h))


cam_handle = None
mech_handles = []
for h in handles:
    o = obj_of(h)
    if o is None:
        continue
    if o.get_class().get_name() == 'CameraComponent':
        cam_handle = h
    if o.get_name().startswith('MechVM_'):
        mech_handles.append(h)
if cam_handle is None:
    raise RuntimeError('CameraComponent not found in BP_Camera')

for h in mech_handles:
    try:
        sds.delete_subobject(handles[0], h, bp)
    except Exception as ex:
        print('delete prior MechVM_ err:', ex)

m_mech = unreal.load_asset('/Game/AlienSkies/Materials/M_MechHybrid')
for comp_name, mesh_name in PARTS:
    params = unreal.AddNewSubobjectParams(parent_handle=cam_handle,
                                          new_class=unreal.StaticMeshComponent,
                                          blueprint_context=bp)
    h, fail = sds.add_new_subobject(params)
    if fail and not fail.is_empty():
        print('add fail', comp_name, fail)
        continue
    sds.rename_subobject(h, unreal.Text(comp_name))
    comp = obj_of(h)
    comp.set_editor_property('static_mesh', unreal.load_asset(f'{MECH}/{mesh_name}'))
    comp.set_editor_property('relative_location', RIG_OFFSET)
    comp.set_editor_property('relative_rotation', RIG_ROT)
    comp.set_editor_property('relative_scale3d', unreal.Vector(RIG_SCALE, RIG_SCALE, RIG_SCALE))
    comp.set_editor_property('cast_shadow', False)
    if m_mech:
        comp.set_material(0, m_mech)
    print('added', comp_name)

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(BP_PATH)

# clear the old stranded per-instance actors
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('MechViewmodel'):
        eas.destroy_actor(a)
les.save_current_level()
print('BP viewmodel baked into BP_Camera + level cleaned.')
