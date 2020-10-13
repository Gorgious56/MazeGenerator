"""
This module should be deprecated soon enough
"""

import bpy
from ..managers import mesh_manager, object_manager, grid_manager, modifier_manager
from ..maze_logic.algorithms import manager as algorithm_manager
from ..shading.objects import manager as mat_creator
from ..shading import textures as texture_manager


class MazeVisual:
    """
    This class does way too much things
    """
    scene = None
    props = None

    def refresh_maze(scene: bpy.types.Scene) -> None:
        MazeVisual.scene = scene
        MazeVisual.props = scene.mg_props
        object_manager.ObjectManager.get_or_create_and_link_objects(scene)
        mesh_manager.MeshManager.create_vertex_groups(
            object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)
        modifier_manager.setup_modifiers_and_drivers(
            MazeVisual, object_manager.ObjectManager, MazeVisual.props.textures.displacement)

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

            object_manager.ObjectManager.get_or_create_and_link_objects(scene)
            object_manager.ObjectManager.update_wall_visibility(
                props, algorithm_manager.is_algo_weaved(props))

            texture_manager.generate_textures(bpy.data.textures, props)

            grid_manager.GridManager.grid.calc_distances(props)
            mesh_manager.MeshManager.create_vertex_groups(
                object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)
            mesh_manager.MeshManager.build_objects(
                props, grid_manager.GridManager.grid, object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)

            modifier_manager.setup_modifiers_and_drivers(
                MazeVisual, object_manager.ObjectManager, props.textures.displacement)

            mat_creator.create_materials(props, object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)
