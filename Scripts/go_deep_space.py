"""Make the editor viewport actually match deep space (and match my SceneCapture
screenshots). Root-cause fixes for the milky/washed look + visible terrain:

1. DELETE SkyAtmosphere + ExponentialHeightFog (the horizon band / planet glow).
2. DELETE Landscape + all LandscapeStreamingProxy (the mountain). WP streams the
   proxies back if you just move them, so we destroy them.
3. Add an unbounded PostProcessVolume with LOCKED exposure (no eye-adaptation
   brightening of the dim scene) + tamed bloom so galaxies don't blow to white.
"""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def by_class(cls):
    return [a for a in eas.get_all_level_actors() if a.get_class().get_name() == cls]


# ---------- 1 + 2: delete atmosphere, fog, landscape ----------
deleted = 0
# WorldPartitionHLOD = baked low-detail landscape proxies; they keep rendering the
# terrain (the bottom band) even after the source Landscape is deleted.
for cls in ('SkyAtmosphere', 'ExponentialHeightFog', 'Landscape',
            'LandscapeStreamingProxy', 'WorldPartitionHLOD'):
    for a in by_class(cls):
        eas.destroy_actor(a)
        deleted += 1
print(f'Deleted {deleted} atmosphere/fog/landscape/HLOD actors')

# ---------- 3: PostProcessVolume with locked exposure ----------
# Remove any old one we made
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'PPV_DeepSpace':
        eas.destroy_actor(a)

ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
ppv.set_actor_label('PPV_DeepSpace')
ppv.set_editor_property('unbound', True)  # affects whole world regardless of bounds

s = ppv.get_editor_property('settings')
# Lock exposure: manual method + fixed bias => no auto-brightening of dark space
s.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL)
s.set_editor_property('auto_exposure_bias', 11.0)  # EV100; manual exposure level
# Belt-and-suspenders: also clamp histogram min==max in case manual is ignored
s.set_editor_property('auto_exposure_min_brightness', 1.0)
s.set_editor_property('auto_exposure_max_brightness', 1.0)
# Tame bloom so additive galaxies keep their shape/color instead of white blobs
s.set_editor_property('bloom_intensity', 0.35)
s.set_editor_property('bloom_threshold', 1.0)
# Enable the overrides so the settings actually apply
s.set_editor_property('override_auto_exposure_method', True)
s.set_editor_property('override_auto_exposure_bias', True)
s.set_editor_property('override_auto_exposure_min_brightness', True)
s.set_editor_property('override_auto_exposure_max_brightness', True)
s.set_editor_property('override_bloom_intensity', True)
s.set_editor_property('override_bloom_threshold', True)
ppv.set_editor_property('settings', s)

les.editor_invalidate_viewports()
saved = les.save_current_level()
print(f'PPV_DeepSpace added (locked exposure, tamed bloom). Saved: {saved}')
