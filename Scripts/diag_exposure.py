"""Inspect auto-exposure / eye-adaptation settings on PostProcessVolumes and any global PP.
Read-only diagnosis."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
found = False
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    if 'PostProcess' in cls or cls == 'ExponentialHeightFog':
        found = True
        print(f'--- {a.get_actor_label()} ({cls}) ---')
        try:
            comp = a.get_component_by_class(unreal.PostProcessComponent)
        except Exception:
            comp = None
        if comp is None and hasattr(a, 'settings'):
            settings = a.settings
        else:
            settings = comp.settings if comp else None
        if settings is None:
            try:
                settings = a.get_editor_property('settings')
            except Exception:
                settings = None
        if settings:
            for key in ['override_auto_exposure_method','auto_exposure_method',
                        'override_auto_exposure_min_brightness','auto_exposure_min_brightness',
                        'override_auto_exposure_max_brightness','auto_exposure_max_brightness',
                        'override_auto_exposure_bias','auto_exposure_bias',
                        'override_auto_exposure_speed_down','auto_exposure_speed_down']:
                try:
                    print(f'  {key} = {settings.get_editor_property(key)}')
                except Exception as e:
                    pass
if not found:
    print('No PostProcessVolume found in level. Exposure = project/default (auto-exposure ON by default).')
print('Done.')
