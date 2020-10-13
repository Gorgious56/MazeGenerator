"""
This module should be deprecated soon enough
"""

import bpy
from ..managers import mesh_manager, grid_manager, modifier_manager
from ..maze_logic.algorithms import manager as algorithm_manager
from ..shading.objects import manager as mat_creator
from ..shading import textures as texture_manager
from ..blender_logic.objects import get_or_create_and_link_objects, update_wall_visibility


class MazeVisual:
    """
    This class does way too much things
    """
    scene = None
    props = None

    @staticmethod
    def refresh_maze(scene: bpy.types.Scene) -> None:
        props = scene.mg_props
        MazeVisual.scene = scene
        MazeVisual.props = scene.mg_props
        get_or_create_and_link_objects(scene)
        mesh_manager.MeshManager.create_vertex_groups(
            props.objects.cells, props.objects.walls)
        modifier_manager.setup_modifiers_and_drivers(scene, props)

    @staticmethod
    def generate_maze(scene: bpy.types.Scene) -> None:
        self = MazeVisual
        self.scene = scene
        self.props = scene.mg_props
        props = self.props

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
