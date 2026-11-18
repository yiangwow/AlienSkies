"""Drop galaxy brightness so the new sharp-arm material doesn't blow out.
Hero/near: 3.0, scatter: 2.5, far dim: 1.8. No respawn needed."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
les   = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
updated = 0
for a in actors:
    lbl = a.get_actor_label()
    if not lbl.startswith('Galaxy_'):
        continue
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    if not smc:
        continue
    mid = smc.get_material(0)
    if not mid:
        continue
    if lbl in ('Galaxy_Hero', 'Galaxy_Blue', 'Galaxy_Red', 'Galaxy_Far'):
        b = 3.0
    elif lbl.startswith('Galaxy_N'):
        b = 3.2
    elif lbl.startswith('Galaxy_F'):
        b = 2.5
    elif lbl.startswith('Galaxy_D'):
        b = 1.8
    else:
        b = 2.5
    try:
        mid.set_scalar_parameter_value('Brightness', b)
        updated += 1
    except Exception:
        pass

les.save_current_level()
print(f'Updated brightness on {updated} galaxies.')
