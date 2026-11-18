"""Revert photon ring to the thin rim (image #8 state): radius = SHADOW_R*1.06 (~33920).
The 44000 fat ring read as a fake blown-out donut."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ring = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_PhotonRing': ring = a
if ring is None:
    print('PhotonRing not found - PIE/Standalone running?')
else:
    R = 32000.0 * 1.06   # 33920, thin rim hugging the 32000 core
    ring.set_actor_scale3d(unreal.Vector(R/50.0, R/50.0, R/50.0))
    les.save_current_level()
    print(f'Reverted photon ring radius -> {R}, saved.')
