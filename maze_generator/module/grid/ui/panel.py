"""
Parameters Panel
"""


import bpy
from maze_generator.module.cell.constants import CellType
from maze_generator.module.space_representation.constants import SpaceRepresentation
from maze_generator.module.grid.operators.op_tweak_maze_size import MG_OT_TweakMazeSize


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
        cell_props = mg_props.cell_props

        if cell_props.is_a(CellType.POLAR) and mg_props.space_rep_props.representation in (
            SpaceRepresentation.CYLINDER.value,
            SpaceRepresentation.MOEBIUS.value,
            SpaceRepresentation.TORUS.value,
        ):
            layout.label(text="Only Regular and Stairs for Polar cells", icon="ERROR")
        elif (
            cell_props.is_a(CellType.TRIANGLE) or cell_props.is_a(CellType.HEXAGON) or cell_props.is_a(CellType.OCTOGON)
        ):
            if mg_props.space_rep_props.representation in (
                SpaceRepresentation.CYLINDER.value,
                SpaceRepresentation.MOEBIUS.value,
                SpaceRepresentation.TORUS.value,
            ):
                layout.label(text="Needs PAIR Columns (2, 4, 6, ...)", icon="ERROR")
            if (
                mg_props.space_rep_props.representation == SpaceRepresentation.MOEBIUS.value
                and mg_props.maze_columns <= 5 * mg_props.maze_rows_or_radius
            ):
                layout.label(text="Set Columns > 5 * Rows", icon="ERROR")
            elif (
                mg_props.space_rep_props.representation == SpaceRepresentation.TORUS.value
                and mg_props.maze_columns > mg_props.maze_rows_or_radius
            ):
                layout.label(text="Set Rows > Columns", icon="ERROR")
        elif (
            mg_props.space_rep_props.representation == SpaceRepresentation.MOEBIUS.value
            and mg_props.maze_columns <= 3 * mg_props.maze_rows_or_radius
        ):
            layout.label(text="Set Columns > 3 * Rows", icon="ERROR")
        elif (
            mg_props.space_rep_props.representation == SpaceRepresentation.TORUS.value
            and 2 * mg_props.maze_columns > mg_props.maze_rows_or_radius
        ):
            layout.label(text="Set Rows > 2 * Columns", icon="ERROR")
        elif mg_props.space_rep_props.representation == SpaceRepresentation.BOX.value:
            layout.label(text="Dimensions are 1 face of the cube", icon="QUESTION")

        def maze_size_ui(prop_name, decrease, increase, text):
            row = layout.row(align=True)
            sub = row.row()
            sub.operator(MG_OT_TweakMazeSize.bl_idname, text="", icon="REMOVE").tweak_size = decrease

            sub = row.row()
            sub.prop(mg_props, prop_name, slider=True, text=text)
            sub.scale_x = 10.0

            sub = row.row()
            sub.operator(MG_OT_TweakMazeSize.bl_idname, text="", icon="ADD").tweak_size = increase
            return row

        if cell_props.is_a(CellType.POLAR):
            layout.prop(mg_props, "maze_polar_branch", text="Branch amount")
        else:
            maze_size_ui("maze_columns", [-1, 0, 0], [1, 0, 0], "Columns")

        # row = layout.row()
        # row.prop(mg_props, "maze_columns")
        # row.active = False

        row = maze_size_ui("maze_rows_or_radius", [0, -1, 0], [0, 1, 0], "Rows").enabled = True
        