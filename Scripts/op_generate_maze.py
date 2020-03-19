from bpy.types import Operator
import bpy
from . maze_logic . data_structure import grid
from . maze_logic . algorithms import algorithm_manager
from . utils . modifier_manager import add_modifier


class GenerateMazeOperator(Operator):
    """Tooltip"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.rows_or_radius > 0

    def execute(self, context):
        self.main(context)
        return {'FINISHED'}

    def main(self, context):
        scene = context.scene
        mg_props = scene.mg_props

        g = grid.Grid(mg_props.rows_or_radius, mg_props.rows_or_radius)
        algorithm_manager.work(mg_props.maze_algorithm, g, mg_props.seed)

        self.set_walls(scene, mg_props, g.get_all_walls())

    def set_walls(self, scene, mg_props, all_walls):
        # Get or add the Wall mesh
        try:
            mesh_wall = bpy.data.meshes['Wall Mesh']
            mesh_wall.clear_geometry()
        except KeyError:
            mesh_wall = bpy.data.meshes.new("Wall Mesh")

        # Get or add the Wall object and link it to the wall mesh
        try:
            obj_wall = scene.objects['Wall']
        except KeyError:
            obj_wall = bpy.data.objects.new('Wall', mesh_wall)
            scene.collection.objects.link(obj_wall)

        add_modifier(obj_wall, 'WELD', 'Weld')
        add_modifier(obj_wall, 'SCREW', 'Screw')
        obj_wall.modifiers['Screw'].angle = 0
        obj_wall.modifiers['Screw'].steps = 2
        obj_wall.modifiers['Screw'].render_steps = 2
        obj_wall.modifiers['Screw'].screw_offset = mg_props.wall_height
        obj_wall.modifiers["Screw"].use_smooth_shade = False
        add_modifier(obj_wall, 'SOLIDIFY', 'Solidify')
        obj_wall.modifiers["Solidify"].solidify_mode = 'NON_MANIFOLD'
        obj_wall.modifiers["Solidify"].thickness = mg_props.wall_width
        obj_wall.modifiers["Solidify"].offset = 0

        mesh_wall.from_pydata(
            all_walls,
            [(i, i + 1) for i in range(0, len(all_walls) - 1, 2)],
            [])
