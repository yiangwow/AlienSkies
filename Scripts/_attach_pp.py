"""Attach M_PPLensing as a blendable on PPV_DeepSpace so it renders in the editor
viewport / PIE (post-process materials don't show in SceneCapture)."""
import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mat=unreal.load_asset('/Game/AlienSkies/Materials/M_PPLensing')
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='PPV_DeepSpace':
        s=a.get_editor_property('settings')
        wbs=s.get_editor_property('weighted_blendables')
        keep=[b for b in list(wbs.get_editor_property('array')) if b.get_editor_property('object')!=mat]
        wb=unreal.WeightedBlendable(); wb.set_editor_property('weight',1.0); wb.set_editor_property('object',mat)
        nb=unreal.WeightedBlendables(); nb.set_editor_property('array',keep+[wb])
        s.set_editor_property('weighted_blendables',nb); a.set_editor_property('settings',s)
        print('attached M_PPLensing to PPV (total blendables:',len(keep)+1,')')
les.save_current_level()
