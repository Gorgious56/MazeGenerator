from bpy.types import Operator
from time import time
from . visual . grid_visual import GridVisual


class GenerateMazeOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.rows_or_radius > 0 and context.mode == 'OBJECT'

    def execute(self, context):
        start_time = time()
        self.main(context)
        print(str((time() - start_time) * 1000).split('.')[0] + ' ms')
        return {'FINISHED'}

    def main(self, context):
        if context.mode == 'OBJECT':
            GridVisual(context.scene)
