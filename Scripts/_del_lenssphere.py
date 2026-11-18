"""Delete the redundant M_Lensing sphere (BlackHole_Lensing) — the post-process lens
now does the wrapping, and the sphere only adds a flat circle outline + refraction band
artifacts. Reversible via build_lensing.py."""
import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
n=0
for a in eas.get_all_level_actors():
    if a.get_actor_label()=='BlackHole_Lensing':
        eas.destroy_actor(a); n+=1
les.save_current_level()
print('deleted BlackHole_Lensing x',n)
