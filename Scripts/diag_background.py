"""List background-ish actors (skybox, starfield, nebula, galaxies) and whether hidden.
Also report the corona sphere radius and camera-inside test for a few distances."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
keys = ('star','nebula','sky','galax','background','bg','milky','dust','field')
print('=== background-ish actors ===')
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    low = lbl.lower()
    if any(k in low for k in keys):
        hidden = a.is_hidden_ed()
        try: rt_hidden = a.get_editor_property('hidden')
        except Exception: rt_hidden = '?'
        print(f'  {lbl:32s} hidden_ed={hidden} actor_hidden={rt_hidden}')
print('=== black hole / corona actors ===')
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith('BlackHole_'):
        s = a.get_actor_scale3d()
        print(f'  {lbl:32s} scale=({s.x:.0f},{s.y:.0f},{s.z:.0f})  ~radius={s.x*50:.0f}')
print('Done.')
