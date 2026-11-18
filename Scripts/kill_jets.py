"""The thin vertical spike at the pole is a jet. Hide robustly in BOTH editor and game
(is_hidden_ed + hidden). List jet state before/after to confirm."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
jets = []
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith('BlackHole_Jet'):
        jets.append(a)
        print(f'before: {lbl} hidden_ed={a.is_hidden_ed()} hidden={a.get_editor_property("hidden")}')
for a in jets:
    a.set_is_temporarily_hidden_in_editor(True)
    a.set_editor_property('hidden', True)
    a.set_actor_hidden_in_game(True)
les.save_current_level()
for a in jets:
    print(f'after:  {a.get_actor_label()} hidden_ed={a.is_hidden_ed()} hidden={a.get_editor_property("hidden")}')
print(f'Hid {len(jets)} jet actors. Saved.')
