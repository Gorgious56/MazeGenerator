import bpy


class ObjectsPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the objects
    """

    walls: bpy.props.PointerProperty(name="Wall Object", type=bpy.types.Object)
    cells: bpy.props.PointerProperty(name="Cells Object", type=bpy.types.Object)
    cylinder: bpy.props.PointerProperty(name="Cylinder Object", type=bpy.types.Object)
    torus: bpy.props.PointerProperty(name="Torus Object", type=bpy.types.Object)
    thickness_shrinkwrap: bpy.props.PointerProperty(name="Empty Object helping shrinkwrapping", type=bpy.types.Object)
