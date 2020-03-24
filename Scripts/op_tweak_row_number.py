from bpy.types import Operator
from bpy.props import BoolProperty


class TweakRowNumberOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.tweak_row_number"
    bl_label = "Tweak Row Number"

    add_or_remove: BoolProperty(
        name="Add or remove row",
        default=False,
    )

    def execute(self, context):
        context.scene.mg_props.rows_or_radius += 1 if self.add_or_remove else - 1
        return {'FINISHED'}
