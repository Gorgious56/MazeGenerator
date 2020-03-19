import bpy


def main(context):
    for i, ob in enumerate(context.scene.objects):
        ob.name = str(i)


class GenerateMazeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(GenerateMazeOperator)


def unregister():
    bpy.utils.unregister_class(GenerateMazeOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.maze.generate()
