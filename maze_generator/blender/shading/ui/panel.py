"""
Display Panel
"""

import bpy
from maze_generator.blender.shading.material.nodes import node_from_mat
from maze_generator.blender.object.cells import shading as shading_cells


class DisplayPanel(bpy.types.Panel):
    """
    Display Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_DisplayPanel"
    bl_label = "Display"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    def draw_header(self, context):
        self.layout.label(text="", icon="BRUSH_DATA")

    def draw(self, context):
        layout = self.layout
        mg_props = context.scene.mg_props

        box = layout.box()
        box.prop(mg_props.display, "paint_style")
        row = box.row(align=True)
        row.prop(mg_props.display, "show_longest_path", text="Solution", toggle=True)
        obj_cells = mg_props.objects.cells
        if obj_cells:
            try:  # TODO get rid of try/except
                longest_path_mask_mod = obj_cells.modifiers.get(mg_props.mod_names.mask_longest_path)
                if longest_path_mask_mod:
                    row_2 = row.row()
                    row_2.prop(longest_path_mask_mod, "show_viewport", text="Hide Rest", toggle=True)
                    row_2.enabled = mg_props.display.show_longest_path
            except ReferenceError:
                pass
        cell_mat = mg_props.display.materials.cell
        if mg_props.display.paint_style == "UNIFORM":
            cell_rgb_node = node_from_mat(cell_mat, shading_cells.NodeNames.rgb)
            if cell_rgb_node:
                box.prop(cell_rgb_node.outputs[0], "default_value", text="Color")
        else:
            row = box.row(align=True)
            cell_color_ramp_node = node_from_mat(cell_mat, shading_cells.NodeNames.cr_distance)
            if cell_color_ramp_node:
                row.box().template_color_ramp(cell_color_ramp_node, property="color_ramp", expand=True)

        cell_hsv_node = node_from_mat(cell_mat, shading_cells.NodeNames.hsv)
        if cell_hsv_node:
            box.prop(cell_hsv_node.inputs[0], "default_value", text="Hue Shift", slider=True)
            box.prop(cell_hsv_node.inputs[1], "default_value", text="Saturation Shift", slider=True)
            box.prop(cell_hsv_node.inputs[2], "default_value", text="Value Shift", slider=True)
