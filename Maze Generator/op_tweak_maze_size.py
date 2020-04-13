from bpy.types import Operator
from bpy.props import IntVectorProperty


class TweakMazeSizeOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.tweak_maze_size"
    bl_label = "Tweak Row Number"

    tweak_size: IntVectorProperty(
        name="Tweak the maze size dimension",
    )

    def execute(self, context):
        if self.tweak_size[0] != 0:
            context.scene.mg_props.maze_columns += self.tweak_size[0]
        elif self.tweak_size[1] != 0:
            context.scene.mg_props.maze_rows_or_radius += self.tweak_size[1]
        elif self.tweak_size[2] != 0:
            context.scene.mg_props.maze_levels += self.tweak_size[2]
        return {'FINISHED'}
