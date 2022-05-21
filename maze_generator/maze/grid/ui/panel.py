"""
Parameters Panel
"""


import bpy
from maze_generator.maze.cell.constants import CellType


class ParametersPanel(bpy.types.Panel):
    """
    Grid Parameters Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_ParametersPanel"
    bl_label = "Grid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    def draw_header(self, context):
        self.layout.label(text="", icon="PREFERENCES")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props

        if mg_props.cell_props.is_a(CellType.POLAR):
            layout.prop(mg_props.maze, "polar_branch", text="Branch amount")
        else:
            layout.prop(mg_props.maze, "columns", text="Columns")

        layout.prop(mg_props.maze, "rows_or_radius", text="Rows")
        layout.prop(mg_props.maze, "random_cells_geomery", text="Random Cells", slider=True)
