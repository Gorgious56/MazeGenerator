from bpy.types import Operator
from bpy.props import IntProperty
from time import time
from . visual . grid_visual import GridVisual


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
            GridVisual(context.scene)
        context.scene.mg_props.generation_time = int((time() - start_time) * 1000)
        return {'FINISHED'}
        
