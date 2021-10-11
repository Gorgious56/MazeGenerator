"""
Cells Panel
"""

import bpy
from maze_generator.module.cell.constants import CellType


class CellsPanel(bpy.types.Panel):
    """
    Cells Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_CellsPanel"
    bl_label = " "
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    @classmethod
    def poll(cls, context):
        return context.scene.mg_props.objects.cells

    def draw_header(self, context):
        self.layout.label(text="Cells", icon="TEXTURE_DATA")
        try:
            cells = context.scene.objects["MG_Cells"]
            self.layout.prop(cells, "hide_viewport", text="")
            self.layout.prop(cells, "hide_render", text="")
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props
    
        cell_props = mg_props.cell_props
        cell_enum_icon = {
            CellType.POLAR.value: "MESH_CIRCLE",
            CellType.TRIANGLE.value: "OUTLINER_OB_MESH",
            CellType.HEXAGON.value: "SEQ_CHROMA_SCOPE",
            CellType.OCTOGON.value: "MESH_ICOSPHERE",
        }.get(cell_props.type, "MESH_PLANE")

        layout.prop(cell_props, "type", icon=cell_enum_icon, text="Cell")
        box = layout.box()

        try:
            obj_cells = mg_props.objects.cells
            cell_thickness_mod = obj_cells.modifiers[mg_props.mod_names.thickness_disp]
            cell_wire_mod = obj_cells.modifiers[mg_props.mod_names.wireframe]
            cell_bevel_mod = obj_cells.modifiers[mg_props.mod_names.bevel]
            cell_subdiv_mod = obj_cells.modifiers[mg_props.mod_names.subdiv]
            cell_stairs = obj_cells.modifiers[mg_props.mod_names.stairs]
        except (ReferenceError, KeyError):
            return

        box.prop(mg_props.cell_props, "inset", slider=True, text="Inset")
        row = box.row(align=True)
        row.prop(cell_thickness_mod, "strength", text="Thickness")
        if cell_stairs.strength != 0:
            row.prop(mg_props, "maze_basement", text="Basement", toggle=True)
        row = box.row(align=True)
        row.prop(cell_subdiv_mod, "levels", text="Subdiv")
        row.prop(mg_props.cell_props, "cell_decimate", slider=True, text="Decimate", icon="MOD_DECIM")

        box.prop(mg_props.meshes, "use_smooth", toggle=True, icon="SHADING_RENDERED", text="Shade Smooth")

        if cell_subdiv_mod.levels > 0 and (cell_bevel_mod.width > 0 or cell_wire_mod.thickness > 0):
            box.label(text="Bevel conflicts with Subdivision", icon="ERROR")

        box = layout.box()
        box.label(text="Contour")

        row = box.row(align=True)

        bevel_row = row.row()
        bevel_row.prop(cell_bevel_mod, "width", text="Bevel")
        bevel_row.enabled = cell_wire_mod.thickness == 0

        wireframe_row = row.row()
        wireframe_row.prop(cell_wire_mod, "thickness", slider=True, text="Wireframe")
        wireframe_row.enabled = obj_cells.modifiers[mg_props.mod_names.bevel].width == 0

        row = box.row(align=True)
        row.prop(mg_props.cell_props, "cell_contour_black", toggle=True, text="Black Outline")

        replace_row = row.row()
        replace_row.prop(cell_wire_mod, "use_replace", toggle=True)
        replace_row.enabled = cell_wire_mod.thickness > 0

        if (cell_wire_mod.thickness > 0 or cell_bevel_mod.width > 0) and mg_props.cell_props.inset < 0.1:
            box.label(text="Set Inset > 0,1", icon="ERROR")
        if cell_bevel_mod.width > 0 and (cell_thickness_mod.strength == 0 and not mg_props.maze_basement):
            box.label(text="Set Cell Thickness != 0 or Toggle Basement", icon="ERROR")
