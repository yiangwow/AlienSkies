"""Editor-only: hide the lensing sphere + jets + photon ring to evaluate the PP lens
against just the disk + black core. Run _unhide.py (or this with --show) to restore."""
import unreal, sys
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
HIDE = {'BlackHole_Lensing','BlackHole_JetN','BlackHole_JetS',
        'BlackHole_JetSheathN','BlackHole_JetSheathS','BlackHole_PhotonRing'}
show = '--show' in sys.argv
for a in eas.get_all_level_actors():
    if a.get_actor_label() in HIDE:
        a.set_is_temporarily_hidden_in_editor(not show)
print('shown' if show else 'hidden', sorted(HIDE))
