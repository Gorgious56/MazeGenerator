from bpy.types import Operator
from time import time
from . visual . maze_visual import MazeVisual


class GenerateMazeOperator(Operator):
    """Generate a new maze"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.rows_or_radius > 0 and context.mode == 'OBJECT'

    def execute(self, context):
        start_time = time()
        if context.mode == 'OBJECT':
            MazeVisual(context.scene)
        context.scene.mg_props.generation_time = int((time() - start_time) * 1000)
        return {'FINISHED'}
