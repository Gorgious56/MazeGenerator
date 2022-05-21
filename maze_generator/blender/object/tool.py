"""
This modules stores methods and properties related to Blender objects and collections
"""
import bpy


def get_or_create(name: str, container: bpy.types.Collection = None):
    if container is None:
        container_obj = bpy.data
        container = bpy.context.scene.collection
    obj = getattr(container_obj, "objects").get(name)
    if obj is None:
        new_mesh = bpy.data.meshes.new(name=name)
        obj = bpy.data.objects.new(name=name, object_data=new_mesh)
        container.objects.link(obj)
    return obj


def get_or_create_mesh_object(props, get_object: callable, obj_attr_name: str, obj_name: str) -> None:
    obj = get_object(obj_name)
    if not obj:
        mesh = bpy.data.meshes.get(obj_name)
        if not mesh:
            mesh = bpy.data.meshes.new(obj_name)
        setattr(props.meshes, obj_attr_name, mesh)
        obj = bpy.data.objects.new(obj_name, mesh)

    setattr(props.objects, obj_attr_name, obj)


def get_or_create_helper(
    props,
    get_object: callable,
    attr_name: str,
    obj_name: str,
    primitive_add=bpy.ops.curve.primitive_bezier_circle_add,
    rot: float = (0, 0, 0),
    attributes=None,
) -> None:
    if not hasattr(props.objects, attr_name):
        return
    obj_get = get_object(obj_name)
    if not obj_get:
        primitive_add(enter_editmode=False, align="WORLD", location=(0, 0, 0), rotation=rot)
        obj_get = bpy.context.active_object
        obj_get.name = obj_name
        obj_get.data.name = obj_name
    setattr(props.objects, attr_name, obj_get)
    if attributes:
        for obj_attr, obj_attr_value in attributes.items():
            setattr(obj_get, obj_attr, obj_attr_value)
    obj_get.hide_viewport = obj_get.hide_render = True
