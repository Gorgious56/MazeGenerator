"""
Parameters Panel
"""


import bpy
from maze_generator.module.cell.constants import CellType
from maze_generator.module.space_representation.constants import SpaceRepresentation


class SpaceRepresentationPanel(bpy.types.Panel):
    """
    Space Representation Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_SpaceRepresentationPanel"
    bl_label = "Space Representation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    def draw_header(self, context):
        self.layout.label(text="", icon="NLA_PUSHDOWN")

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

        space_enum_icon = "MESH_PLANE"
        if mg_props.space_rep_props.representation == SpaceRepresentation.PLANE.value:
            space_enum_icon = "MESH_PLANE"
        if mg_props.space_rep_props.representation == SpaceRepresentation.CYLINDER.value:
            space_enum_icon = "GP_SELECT_STROKES"
        if mg_props.space_rep_props.representation == SpaceRepresentation.MOEBIUS.value:
            space_enum_icon = "GP_SELECT_STROKES"
        if mg_props.space_rep_props.representation == SpaceRepresentation.TORUS.value:
            space_enum_icon = "MESH_CUBE"

        layout.prop(mg_props.space_rep_props, "representation", icon=space_enum_icon, text="Fold")

        obj_cells = mg_props.objects.cells
        if obj_cells:
            try:
                row = layout.row(align=True)
                stairs_mod = obj_cells.modifiers.get(mg_props.mod_names.stairs)
                if stairs_mod:
                    row.prop(stairs_mod, "strength", text="Stairs")

                row = layout.row(align=True)
                tex_disp_mod = obj_cells.modifiers.get("MG_TEX_DISP")
                if tex_disp_mod:
                    row.prop(tex_disp_mod, "strength", text="Inflate", slider=True)
                row.prop(mg_props.textures.displacement, "noise_scale", text="Scale", slider=True)
            except ReferenceError:
                pass
