import bpy

from maze_generator.blender.mesh.vertex_groups.main import get_vg_name, set_vg_name


class VertexGroupsNamesPG(bpy.types.PropertyGroup):
    displace_name: bpy.props.StringProperty(
        name="Displace",
        default="MG_DISPLACE",
        get=lambda self: get_vg_name(self, "displace_name", "MG_DISPLACE"),
        set=lambda self, value: set_vg_name(self, "displace_name", value),
    )
    stairs_name: bpy.props.StringProperty(
        name="Stairs",
        default="MG_STAIRS",
        get=lambda self: get_vg_name(self, "stairs_name", "MG_STAIRS"),
        set=lambda self, value: set_vg_name(self, "stairs_name", value),
    )
    cell_thickness_name: bpy.props.StringProperty(
        name="Cell Thickness",
        default="MG_CELL_THICKNESS",
        get=lambda self: get_vg_name(self, "cell_thickness_name", "MG_CELL_THICKNESS"),
        set=lambda self, value: set_vg_name(self, "cell_thickness_name", value),
    )
    longest_path_name: bpy.props.StringProperty(
        name="Longest Path",
        default="MG_LONGEST_PATH",
        get=lambda self: get_vg_name(self, "longest_path_name", "MG_LONGEST_PATH"),
        set=lambda self, value: set_vg_name(self, "longest_path_name", value),
    )

    @property
    def names(self):
        return [getattr(self, attr) for attr in self.attributes_names]

    attributes_names = (
        "displace_name",
        "stairs_name",
        "cell_thickness_name",
        "longest_path_name",
    )
