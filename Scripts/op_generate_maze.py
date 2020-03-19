from bpy.types import Operator


class GenerateMazeOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.main(context)
        return {'FINISHED'}

    def main(self, context):
        for i, ob in enumerate(context.scene.objects):
            ob.name = str(i)
