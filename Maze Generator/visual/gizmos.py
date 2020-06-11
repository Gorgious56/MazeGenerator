from ..managers.object_manager import ObjectManager as om
from ..managers import modifier_manager as mm
from mathutils import Matrix
from math import pi

from bpy.types import (
    GizmoGroup,
)


class MazeWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_light_test"
    bl_label = "Test Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return om.obj_cells and context.scene.mg_props.show_gizmos

    def register_widget(self, widget, rotation):
        if not hasattr(self, "my_widgets"):
            setattr(self, "my_widgets", {})
        getattr(self, "my_widgets")[widget] = {'rotation': rotation}

    def setup_widget(self, data, prop_name, color=(1, 0, 0), rotation=Matrix.Rotation(0, 4, "X")):
        new_widget = self.gizmos.new("GIZMO_GT_arrow_3d")
        new_widget.target_set_prop("offset", data, prop_name)
        new_widget.draw_style = 'BOX'

        new_widget.color = color
        new_widget.alpha = 1

        new_widget.color_highlight = color[0] + 0.4, color[1] + 0.4, color[2] + 0.4
        new_widget.alpha_highlight = 0.5
        self.register_widget(new_widget, rotation)

    def setup(self, context):
        mg_props = context.scene.mg_props
        self.setup_widget(mg_props, "maze_columns_gizmo", color=(1, 0, 0), rotation=Matrix.Rotation(pi / 2, 4, "Y"))
        self.setup_widget(mg_props, "maze_rows_or_radius_gizmo", color=(0, 1, 0), rotation=Matrix.Rotation(-pi / 2, 4, "X"))
        self.setup_widget(om.obj_cells.modifiers[mm.M_STAIRS], "strength", color=(0, 0, 1))
        self.setup_widget(om.obj_cells.modifiers[mm.M_THICKNESS_DISP], "strength", color=(0, 0, 1), rotation=Matrix.Rotation(pi, 4, "X"))

    def refresh(self, context):
        mg_props = context.scene.mg_props
        if hasattr(self, "my_widgets"):
            widgets = getattr(self, "my_widgets")
            for widget, attributes in widgets.items():
                rotation = attributes['rotation']
                scale = Matrix.Scale(0.5, 4)
                widget.matrix_basis = om.obj_cells.matrix_world.normalized() @ rotation
        # mpr = getattr(self, "column_widget")
