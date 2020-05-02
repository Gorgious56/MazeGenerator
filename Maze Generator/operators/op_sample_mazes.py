from bpy.types import Operator
from ..managers.sample_manager import SampleManager


class SampleMazesOperator(Operator):
    """Samples Mazes (Debug)"""
    bl_idname = "maze.sample"
    bl_label = "Sample Mazes"

    def execute(self, context):
        SampleManager.sample(context)
        return {'FINISHED'}
