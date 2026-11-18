import unreal
SDIR='E:/projects/AlienSkies/Screenshots'
mel=unreal.MaterialEditingLibrary
# trivial RED-emissive PP material
RED='/Game/AlienSkies/Materials/M_PPRedTest'
if unreal.EditorAssetLibrary.does_asset_exist(RED):
    m=unreal.load_asset(RED); mel.delete_all_material_expressions(m)
else:
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_PPRedTest','/Game/AlienSkies/Materials',unreal.Material,unreal.MaterialFactoryNew())
m.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS)
m.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
c=mel.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,0)
c.set_editor_property('constant',unreal.LinearColor(1.0,0.0,0.0,1.0))
mel.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m)

ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
w=ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(w,'Slate.bAllowThrottling 0')
loc,rot=ues.get_level_viewport_camera_info()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

def shoot(name, with_blend):
    rt=unreal.TextureRenderTarget2D(); rt.set_editor_property('size_x',640); rt.set_editor_property('size_y',360)
    rt.set_editor_property('render_target_format',unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    ca=eas.spawn_actor_from_class(unreal.SceneCapture2D,loc,rot); cap=ca.capture_component2d
    cap.set_editor_property('texture_target',rt)
    cap.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('fov_angle',90.0)
    if with_blend:
        cap.set_editor_property('post_process_blend_weight',1.0)
        s=cap.get_editor_property('post_process_settings')
        wb=unreal.WeightedBlendable(); wb.set_editor_property('weight',1.0); wb.set_editor_property('object',m)
        wbs=unreal.WeightedBlendables(); wbs.set_editor_property('array',[wb])
        s.set_editor_property('weighted_blendables',wbs); cap.set_editor_property('post_process_settings',s)
    cap.capture_scene()
    unreal.RenderingLibrary.export_render_target(w,rt,SDIR,name)
    eas.destroy_actor(ca)
    print('shot',name,'with_blend=',with_blend)

shoot('test_noblend.png', False)
shoot('test_red.png', True)
