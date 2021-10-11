import bpy
from ...blender.operators.op_generate_maze import MG_OT_GenerateMaze

def generate_maze(self, context) -> None:
    if context.scene.mg_props.core.auto_update and context.mode == "OBJECT":
        exec(f"bpy.ops.{MG_OT_GenerateMaze.bl_idname}()")
