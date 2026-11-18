"""Did the landscape material assignment actually stick? Inspect."""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    if cls == 'Landscape':
        mat = a.get_editor_property('landscape_material')
        print(f'Landscape "{a.get_actor_label()}": material = {mat.get_path_name() if mat else "None"}')
        # Iterate children too
        try:
            comps = a.get_components_by_class(unreal.LandscapeComponent)
            print(f'  components: {len(comps)}')
            if comps:
                first = comps[0]
                # The component's override material
                ov = first.get_editor_property('material_instance') if hasattr(first, 'material_instance') else None
                print(f'  first component override: {ov}')
        except Exception as e:
            print(f'  err: {e}')
        break  # main landscape only

# Also check editor world
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print(f'World: {world.get_name()}')
