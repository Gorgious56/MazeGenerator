"""
This operator handles calling the gene
"""


from time import time
import bpy
from maze_generator.maze.algorithm.algorithms import (
    is_algo_incompatible,
    is_algo_weaved,
    work,
)
from maze_generator.maze.grid.grids import generate_grid
from maze_generator.maze.pathfinding.grid import calc_distances

from maze_generator.blender.shading.material.main import create_materials
from maze_generator.blender.shading.texture.main import generate_textures
from maze_generator.blender.modifier.main import setup_modifiers
from maze_generator.blender.mesh.main import build_objects
from maze_generator.blender.mesh.vertex_groups.main import ensure_vertex_groups
from maze_generator.blender.driver.main import setup_drivers
from maze_generator.blender.object.main import get_or_create_and_link_objects
from maze_generator.blender.object.walls.viewport import update_wall_visibility

from maze_generator.blender.preferences.helper import get_preferences


class MG_OT_GenerateMaze(bpy.types.Operator):
    """Generate a new maze"""

    bl_idname = "maze.generate"
    bl_label = "Generate Maze"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        mg_props = context.scene.mg_props
        return (
            mg_props.maze_rows_or_radius > 0
            and mg_props.maze_columns > 0
            and mg_props.maze_levels > 0
            and context.mode == "OBJECT"
        )

    def execute(self, context):
        start_time = time()
        if context.mode == "OBJECT":
            self.generate_maze(context)
        context.scene.mg_props.generation_time = int((time() - start_time) * 1000)
        return {"FINISHED"}

    def generate_maze(self, context) -> None:
        addon_prefs = get_preferences(context)
        ao = context.active_object
        scene = context.scene
        props = scene.mg_props

        grid = generate_grid(props)
        props.grid = grid
        grid.mask_cells()
        grid.prepare_grid()
        grid.init_cells_neighbors()
        grid.prepare_union_find()

        if is_algo_incompatible(props):
            return
        work(grid, props)
        grid.calc_state()
        grid.sparse_dead_ends(props.algorithm.sparse_dead_ends, props.algorithm.seed)
        grid.braid_dead_ends(100 - props.algorithm.keep_dead_ends, props.algorithm.seed)

        get_or_create_and_link_objects(scene, addon_prefs)
        update_wall_visibility(props, is_algo_weaved(props))

        generate_textures(bpy.data.textures, props)

        calc_distances(grid, props)

        ensure_vertex_groups(props.objects, addon_prefs.vertex_groups_names)
        build_objects(props, addon_prefs, grid)

        setup_modifiers(scene, props, addon_prefs)
        setup_drivers(scene, props)

        create_materials(scene, props)
        context.view_layer.objects.active = ao
