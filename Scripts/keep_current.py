"""Lock in the CURRENT (good) black-hole look as ground truth from dump_live, with the one
fix: CaptureR 15000 -> 32000 (= core radius) to kill the gold-leak-over-core bug. Sets every
value explicitly so it does NOT matter what is in memory (discards the in-memory Interstellar
params used for the comparison screenshots). Then saves."""
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

def find(lbl):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lbl:
            return a
    return None

core = find('BlackHole_Core'); ring = find('BlackHole_PhotonRing')
disk = find('BlackHole_RMDisk'); sky = find('SM_SkySphere')

# core / ring (current values)
core.set_actor_scale3d(unreal.Vector(200.0, 200.0, 200.0))          # 32000 radius
ring.set_actor_scale3d(unreal.Vector(212.0, 212.0, 212.0))          # 33920 (1.06x)

# disk material (current defaults) + CaptureR fix
dm = disk.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
dm.set_scalar_parameter_value('InnerR', 19500.0)
dm.set_scalar_parameter_value('OuterR', 78000.0)
dm.set_scalar_parameter_value('Thickness', 5460.0)
dm.set_scalar_parameter_value('Spin', 0.3)
dm.set_scalar_parameter_value('Brightness', 0.7)
dm.set_scalar_parameter_value('BoundR', 117000.0)
dm.set_scalar_parameter_value('LensStrength', 16000.0)
dm.set_scalar_parameter_value('CaptureR', 32000.0)                  # FIX: was 15000 (< core)
dm.set_vector_parameter_value('DiskN', unreal.LinearColor(0.5342, 0.0, 0.8454, 0))
dm.set_vector_parameter_value('DiskU', unreal.LinearColor(0.0, 1.0, 0.0, 0))
dm.set_vector_parameter_value('DiskV', unreal.LinearColor(-0.8454, 0.0, 0.5342, 0))
disk.set_actor_scale3d(unreal.Vector(2457.0, 2457.0, 2457.0))

# background
sm = sky.get_component_by_class(unreal.StaticMeshComponent).get_material(0)
sm.set_scalar_parameter_value('DomeBrightness', 0.15)

les.save_current_level()
print('Locked current look. core=32000 ring=33920 CaptureR=32000 DomeBrightness=0.15. Saved.')
