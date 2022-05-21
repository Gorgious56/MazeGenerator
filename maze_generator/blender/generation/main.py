import bpy  # Keep this
from maze_generator.blender.generation.operators.generate_maze import MG_OT_maze_generate

def generate_maze(self, context) -> None:
    if context.scene.mg_props.generation.auto_update and context.mode == "OBJECT":
        exec(f"bpy.ops.{MG_OT_maze_generate.bl_idname}()")
