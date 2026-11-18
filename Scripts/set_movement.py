import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# Snappy PvP-arena feel: high drag (fast stop / sharp turns), high accel (instant response)
PARAMS = {
    'thrust_acceleration': 1200000.0,   # leaps to speed, no heavy ramp
    'drag': 6.0,                        # crisp stop, higher top speed (=accel/drag)
    'boost_multiplier': 2.5,
}

# Set on the BP_Camera class default (persists for all instances)
cam_bp = unreal.load_asset('/Game/AlienSkies/Blueprints/BP_Camera')
cdo = unreal.get_default_object(cam_bp.generated_class())
for k, v in PARAMS.items():
    try:
        cdo.set_editor_property(k, v)
    except Exception as e:
        print(f'CDO {k} err: {e}')
unreal.EditorAssetLibrary.save_loaded_asset(cam_bp)

# Also set on the placed instance (what actually gets possessed) so this session is correct
n = 0
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == 'BP_Camera_C':
        for k, v in PARAMS.items():
            try: a.set_editor_property(k, v)
            except Exception as e: print(f'inst {k} err: {e}')
        n += 1
les.save_current_level()
print(f'Movement set: {PARAMS}  (applied to CDO + {n} placed instance)')
