"""
Parameters Panel
"""


import bpy
from maze_generator.maze.algorithm.algorithms import (
    algorithm_class_from_name, 
    KruskalRandom, 
    is_algo_incompatible,
)


class AlgorithmPanel(bpy.types.Panel):
    """
    Algorithm Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_AlgorithmPanel"
    bl_label = "Algorithm"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    def draw_header(self, context):
        self.layout.label(text="", icon="HAND")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        mg_props = scene.mg_props
        self.layout.prop(context.scene.mg_props.algorithm, "algorithm", icon="HAND", text="Solver")

        algo_incompatibility = is_algo_incompatible(mg_props)
        if algo_incompatibility:
            layout.label(text=algo_incompatibility, icon="ERROR")
        else:
            for setting in algorithm_class_from_name(mg_props.algorithm.algorithm).settings:
                if setting == "weave":
                    # TODO fix weave maze
                    continue
                    if mg_props.algorithm.algorithm == KruskalRandom.name:
                        box.prop(mg_props.maze, "weave", slider=True)
                    else:
                        box.prop(mg_props.maze, "weave_toggle", toggle=True)
                else:
                    layout.prop(mg_props.algorithm, setting)
        
        layout.prop(mg_props.algorithm, "keep_dead_ends", slider=True, text="Dead Ends")
        layout.prop(mg_props.algorithm, "sparse_dead_ends")
        layout.prop(mg_props.algorithm, "seed")
        row = layout.row()
        obj_cells = mg_props.objects.cells
        if obj_cells:
            try:
                cell_mask_mod = obj_cells.modifiers[mg_props.mod_names.mask]
                row.prop(cell_mask_mod, "threshold", text="Steps")
            except (ReferenceError, KeyError):
                pass
