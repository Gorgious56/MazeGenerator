from bpy.types import Operator
from time import time
from ..visual.maze_visual import MazeVisual


class GenerateMazeOperator(Operator):
    """Generate a new maze"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.maze_rows_or_radius > 0 and mg_props.maze_columns > 0 and mg_props.maze_levels > 0 and context.mode == 'OBJECT'

    def execute(self, context):
        start_time = time()
        if context.mode == 'OBJECT':
            MazeVisual.generate_maze(context.scene)
        context.scene.mg_props.generation_time = int((time() - start_time) * 1000)
        return {'FINISHED'}


class RefreshMazeOperator(Operator):
    """Refresh the maze"""
    bl_idname = "maze.refresh"
    bl_label = 'Refresh Maze'

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.maze_rows_or_radius > 0 and mg_props.maze_columns > 0 and mg_props.maze_levels > 0 and context.mode == 'OBJECT'

    def execute(self, context):
        if context.mode == 'OBJECT':
            MazeVisual.refresh_maze(context.scene)
        return {'FINISHED'}
