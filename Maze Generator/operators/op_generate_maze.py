"""
This operator handles calling the gene
"""


from time import time
import bpy
from ..managers import mesh_manager, grid_manager, modifier_manager
from ..maze_logic.algorithms import manager as algorithm_manager
from ..shading.objects import manager as mat_creator
from ..shading import textures as texture_manager
from ..blender_logic.objects import get_or_create_and_link_objects, update_wall_visibility


class GenerateMazeOperator(bpy.types.Operator):
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
            self.generate_maze(context.scene)
        context.scene.mg_props.generation_time = int((time() - start_time) * 1000)
        return {'FINISHED'}

    def generate_maze(self, scene) -> None:
        props = scene.mg_props

        mesh_manager.MeshManager.reset()

        grid_manager.GridManager.generate_grid(props)
        grid_manager.GridManager.grid.mask_cells()
        grid_manager.GridManager.grid.prepare_grid()
        grid_manager.GridManager.grid.init_cells_neighbors()
        grid_manager.GridManager.grid.prepare_union_find()

        if not algorithm_manager.is_algo_incompatible(props):
            algorithm_manager.work(grid_manager.GridManager.grid, props)
            grid_manager.GridManager.grid.calc_state()
            grid_manager.GridManager.grid.sparse_dead_ends(
                props.sparse_dead_ends, props.seed)
            grid_manager.GridManager.grid.braid_dead_ends(
                100 - props.keep_dead_ends, props.seed)

            get_or_create_and_link_objects(scene)
            update_wall_visibility(
                props, algorithm_manager.is_algo_weaved(props))

            texture_manager.generate_textures(bpy.data.textures, props)

            grid_manager.GridManager.grid.calc_distances(props)
            mesh_manager.MeshManager.create_vertex_groups(
                props.objects.cells, props.objects.walls)
            mesh_manager.MeshManager.build_objects(
                props, grid_manager.GridManager.grid)

            modifier_manager.setup_modifiers_and_drivers(scene, props)

            mat_creator.create_materials(props)
