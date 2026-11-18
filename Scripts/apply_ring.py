"""Apply photon ring radius 44000 (rim meets disk edge -> gap closed). Core stays 32000 (void).
CaptureR untouched at 34000 (no gold-fill). Save level."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ring = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'BlackHole_PhotonRing': ring = a
if ring is None:
    print('PhotonRing not found - PIE/Standalone running?')
else:
    R = 44000.0
    ring.set_actor_scale3d(unreal.Vector(R/50.0, R/50.0, R/50.0))
    les.save_current_level()
    print(f'Applied photon ring radius {R}, saved.')
