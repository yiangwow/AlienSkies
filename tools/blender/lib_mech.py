"""Reusable bpy helpers for the mech generator (Blender 5.1)."""
import bpy


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def beveled_box(name, size, location, bevel=0.04, segments=2):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m = o.modifiers.new('bev', 'BEVEL')
    m.width = bevel
    m.segments = segments
    bpy.ops.object.modifier_apply(modifier='bev')
    return o


def cylinder(name, radius, depth, location, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o


def cone(name, r1, r2, depth, location, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=location, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o


def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def set_accent_vertexcolor(obj, mask_value, layer='Accent'):
    """Write a 0/1 accent mask into a POINT color attribute. body -> 0, glow strip -> 1.
    UE's VertexColor node returns white for meshes with NO color data, so EVERY exported part
    must carry this layer or it would glow fully. Sets the layer active so glTF exports it."""
    me = obj.data
    if layer not in me.color_attributes:
        me.color_attributes.new(name=layer, type='FLOAT_COLOR', domain='POINT')
    ca = me.color_attributes[layer]
    for d in ca.data:
        d.color = (mask_value, mask_value, mask_value, 1.0)
    try:
        me.color_attributes.active_color = ca
    except Exception:
        me.color_attributes.active_color_index = me.color_attributes.find(layer)
    return ca


def add_socket(name, location, parent):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    e = bpy.context.active_object
    e.name = name
    e.parent = parent
    return e
