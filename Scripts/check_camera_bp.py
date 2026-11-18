import unreal
cam_bp = unreal.load_asset('/Game/AlienSkies/Blueprints/BP_Camera')
gen = cam_bp.generated_class()
print(f'BP_Camera generated class: {gen.get_name()}')
# Walk parent chain
parent = unreal.get_default_object(gen).get_class()
print(f'CDO class: {parent.get_name()}')
# Parent class via the blueprint
try:
    pc = cam_bp.get_editor_property('parent_class')
    print(f'Blueprint parent_class = {pc.get_name() if pc else None}')
except Exception as e:
    print(f'parent_class err: {e}')

# Is it an AlienCamera?
cdo = unreal.get_default_object(gen)
print(f'is AlienCamera subclass: {isinstance(cdo, unreal.AlienCamera) if hasattr(unreal,"AlienCamera") else "unreal.AlienCamera not exposed"}')
print(f'auto_possess_player (CDO): {cdo.get_editor_property("auto_possess_player")}')
# Tick enabled?
try:
    print(f'actor_tick_enabled (CDO): {cdo.get_editor_property("can_ever_tick") if False else "n/a"}')
except Exception:
    pass
# List components
print(f'root component class: {cdo.root_component.get_class().get_name() if cdo.root_component else None}')
