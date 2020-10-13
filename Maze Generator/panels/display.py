"""
Display Panel
"""

import bpy
from ..managers import modifier_manager as mod_mgr
from ..visual.maze_visual import MazeVisual
from ..shading.nodes import node_from_mat
from ..shading.objects import cells


class DisplayPanel(bpy.types.Panel):
    """
    Display Panel
    """
    bl_idname = "MAZE_GENERATOR_PT_DisplayPanel"
    bl_label = "Display"
    bl_parent_id = 'MAZE_GENERATOR_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MG'
    order = 4

    # @classmethod
    # def poll(cls, context):
    #     objects = context.scene.mg_props.objects
    #     return objects.cells or objects.walls

    def draw_header(self, context):
        self.layout.label(text='', icon='BRUSH_DATA')

    def draw(self, context):
        if not MazeVisual.scene:
            return
        layout = self.layout
        mg_props = context.scene.mg_props

        box = layout.box()
        box.prop(mg_props, 'paint_style')
        row = box.row(align=True)
        row.prop(mg_props, 'show_longest_path',
                 text='Longest Path', toggle=True)
        try:
            longest_path_mask_mod = mg_props.objects.cells.modifiers[mod_mgr.M_MASK_LONGEST_PATH]
            row_2 = row.row()
            row_2.prop(longest_path_mask_mod, 'show_viewport',
                       text='Hide Rest', toggle=True)
            row_2.enabled = mg_props.show_longest_path
        except ReferenceError:
            pass
        cell_mat = mg_props.materials.cell
        if mg_props.paint_style == 'UNIFORM':
            cell_rgb_node = node_from_mat(cell_mat, cells.NodeNames.rgb)
            if cell_rgb_node:
                box.prop(cell_rgb_node.outputs[0],
                         'default_value', text='Color')
        else:
            row = box.row(align=True)
            cell_color_ramp_node = node_from_mat(
                cell_mat, cells.NodeNames.cr_distance)
            if cell_color_ramp_node:
                row.box().template_color_ramp(cell_color_ramp_node,
                                          property="color_ramp", expand=True)

        cell_hsv_node = node_from_mat(cell_mat, cells.NodeNames.hsv)
        if cell_hsv_node:
            box.prop(
                cell_hsv_node.inputs[0], 'default_value', text='Hue Shift', slider=True)
            box.prop(
                cell_hsv_node.inputs[1], 'default_value', text='Saturation Shift', slider=True)
            box.prop(
                cell_hsv_node.inputs[2], 'default_value', text='Value Shift', slider=True)
