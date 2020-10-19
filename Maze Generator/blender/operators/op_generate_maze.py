"""
This operator handles calling the gene
"""


from time import time
import bpy
from ...maze_logic.algorithms import manager as algorithm_manager
from ...maze_logic.grids.manager import generate_grid
from ...blender.shading.objects import manager as mat_creator
from ...blender.shading import textures as texture_manager
from ...blender.objects import get_or_create_and_link_objects, update_wall_visibility
from ...blender.meshes import MeshManager
from ...blender.modifiers import manager as modifier_manager
from ...blender.drivers import manager as driver_manager

class GenerateMazeOperator(bpy.types.Operator):
    """Generate a new maze"""
    bl_idname = "maze.generate"
    bl_label = "Generate Maze"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return mg_props.maze_rows_or_radius > 0 and mg_props.maze_columns > 0 and mg_props.maze_levels > 0 and context.mode == 'OBJECT'

    def execute(self, context):
        start_time = time()
        if context.mode == 'OBJECT':
            self.generate_maze(context.scene)
        context.scene.mg_props.generation_time = int(
            (time() - start_time) * 1000)
        return {'FINISHED'}

    def generate_maze(self, scene) -> None:
        props = scene.mg_props

        MeshManager.reset()

        grid = generate_grid(props)
        props.grid = grid
        grid.mask_cells()
        grid.prepare_grid()
        grid.init_cells_neighbors()
        grid.prepare_union_find()

        if algorithm_manager.is_algo_incompatible(props):
            return
        algorithm_manager.work(grid, props)
        grid.calc_state()
        grid.sparse_dead_ends(props.sparse_dead_ends, props.seed)
        grid.braid_dead_ends(100 - props.keep_dead_ends, props.seed)

        get_or_create_and_link_objects(scene)
        update_wall_visibility(
            props, algorithm_manager.is_algo_weaved(props))

        texture_manager.generate_textures(bpy.data.textures, props)

        grid.calc_distances(props)

        MeshManager.create_vertex_groups(props.objects)
        MeshManager.build_objects(props, grid)

        modifier_manager.setup_modifiers(scene, props)
        driver_manager.setup_drivers(scene, props)

        mat_creator.create_materials(props)
