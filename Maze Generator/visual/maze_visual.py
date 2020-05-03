import bpy
from ..managers import algorithm_manager, texture_manager, material_manager, mesh_manager, object_manager, grid_manager, modifier_manager


class MazeVisual:
    scene = None
    props = None

    def refresh_maze(scene: bpy.types.Scene) -> None:
        MazeVisual.scene = scene
        MazeVisual.props = scene.mg_props
        object_manager.ObjectManager.get_or_create_and_link_objects(scene)
        texture_manager.TextureManager.generate_textures(bpy.data.textures)
        material_manager.MaterialManager.set_materials(MazeVisual.props, scene)
        mesh_manager.MeshManager.create_vertex_groups(object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)
        modifier_manager.setup_modifiers_and_drivers(MazeVisual, object_manager.ObjectManager, texture_manager.TextureManager)

    def generate_maze(scene: bpy.types.Scene) -> None:
        self = MazeVisual
        self.scene = scene
        self.props = scene.mg_props
        props = self.props

        mesh_manager.MeshManager.reset()

        grid_manager.GridManager.generate_grid(self.props)
        grid_manager.GridManager.grid.new_cell_evt += lambda grid, cell: mesh_manager.MeshManager.on_new_cell(grid, cell)
        grid_manager.GridManager.grid.prepare_grid()
        grid_manager.GridManager.grid.init_cells_neighbors()

        if not algorithm_manager.is_algo_incompatible(props):
            algorithm_manager.work(grid_manager.GridManager.grid, props)
            grid_manager.GridManager.grid.sparse_dead_ends(props.sparse_dead_ends, props.seed)
            grid_manager.GridManager.grid.braid_dead_ends(props.braid_dead_ends, props.seed)

            object_manager.ObjectManager.get_or_create_and_link_objects(scene)
            object_manager.ObjectManager.update_wall_visibility(self.props, algorithm_manager.is_algo_weaved(self.props))

            texture_manager.TextureManager.generate_textures(bpy.data.textures)

            grid_manager.GridManager.grid.calc_distances(self.props)
            mesh_manager.MeshManager.create_vertex_groups(object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)
            mesh_manager.MeshManager.build_objects(props, grid_manager.GridManager.grid, object_manager.ObjectManager.obj_cells, object_manager.ObjectManager.obj_walls)

            modifier_manager.setup_modifiers_and_drivers(MazeVisual, object_manager.ObjectManager, texture_manager.TextureManager)

            material_manager.MaterialManager.set_materials(props, self.scene)
