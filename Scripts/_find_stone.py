"""Dig into the mystery Actor at origin + check for hidden/game-visible stone mesh."""
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)

for a in actors:
    lbl = a.get_actor_label()
    cls = a.get_class().get_name()
    loc = a.get_actor_location()

    # Print ALL components for the bare 'Actor' at origin
    if cls == 'Actor' and abs(loc.x) < 100 and abs(loc.y) < 100 and abs(loc.z) < 100:
        print(f'=== Actor at origin: {lbl} ===')
        comps = a.get_components_by_class(unreal.ActorComponent)
        for c in comps:
            cn = c.get_class().get_name()
            print(f'  Component: {cn}')
            if 'StaticMesh' in cn:
                m = c.get_editor_property('static_mesh')
                print(f'    Mesh: {m.get_path_name() if m else None}')
                mats = c.get_materials()
                for i, mat in enumerate(mats):
                    print(f'    Mat[{i}]: {mat.get_path_name() if mat else None}')

    # Check if any actor is hidden in game
    try:
        hig = a.get_editor_property('b_hidden')
        if hig:
            print(f'  b_hidden=True: {lbl} ({cls})')
    except Exception:
        pass

# Also check SM_SkySphere material slots
for a in actors:
    if a.get_actor_label() == 'SM_SkySphere':
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if smc:
            m = smc.get_editor_property('static_mesh')
            print(f'\nSM_SkySphere mesh: {m.get_path_name() if m else None}')
            mats = smc.get_materials()
            for i, mat in enumerate(mats):
                print(f'  Mat[{i}]: {mat.get_path_name() if mat else None}')
