import bpy
from maze_generator.blender.mesh.helper import update_mesh_smooth


def update_smooth_all_meshes(self):
    for mesh in (self.cells, self.walls):
        update_mesh_smooth(mesh, self.use_smooth)


class MeshesPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the meshes used in the add-on
    """

    walls: bpy.props.PointerProperty(name="Wall Mesh", type=bpy.types.Mesh)
    cells: bpy.props.PointerProperty(name="Cells Mesh", type=bpy.types.Mesh)

    use_smooth: bpy.props.BoolProperty(
        name="Smooth Shade Meshes",
        description="Enforce smooth shading everytime the maze is generated",
        default=False,
        update=lambda self, context: update_smooth_all_meshes(self),
    )

    def update_smooth(self):
        update_smooth_all_meshes(self)


class VerticesRangeInfo:
    def __init__(self, _range, relative_distance, is_longest_path, cell_group, links) -> None:
        self.range = _range
        self.relative_distance = relative_distance
        self.is_longest_path = is_longest_path
        self.cell_group = cell_group
        self.links = links
