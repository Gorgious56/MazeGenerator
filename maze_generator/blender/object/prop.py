import bpy
from maze_generator.blender.object.tool import get_or_create


class ObjectsPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the objects
    """

    main_: bpy.props.PointerProperty(name="Main Object", type=bpy.types.Object)

    @property
    def main(self):
        return self.get("main")

    walls: bpy.props.PointerProperty(name="Wall Object", type=bpy.types.Object)
    cells: bpy.props.PointerProperty(name="Cells Object", type=bpy.types.Object)
    cylinder: bpy.props.PointerProperty(name="Cylinder Object", type=bpy.types.Object)
    torus: bpy.props.PointerProperty(name="Torus Object", type=bpy.types.Object)
    thickness_shrinkwrap: bpy.props.PointerProperty(name="Empty Object helping shrinkwrapping", type=bpy.types.Object)

    @property
    def all(self):
        return (self.wall, self.cells, self.cylinder, self.torus, self.thickness_shrinkwrap)

    def get(self, prop_name):
        return get_or_create(f"MG_{prop_name}".upper())
