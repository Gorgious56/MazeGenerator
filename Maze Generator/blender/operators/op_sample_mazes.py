import time
from bpy.types import Operator
import bpy
import numpy as np
from ...maze_logic import cells
from ...maze_logic.algorithms import manager as algorithm_manager


class SampleMazesOperator(Operator):
    """Samples Mazes (Debug)"""
    bl_idname = "maze.sample"
    bl_label = "Sample Mazes"

    def execute(self, context):
        SampleManager.sample(context)
        return {'FINISHED'}
"""
This module handles automatic generation of mazes with parameters variation
"""




class SampleManager:
    """
    This class handles automatic generation of mazes with parameters variation
    """
    @staticmethod
    def sample(context):
        mg_props = context.scene.mg_props

        prop_save = {}
        for prop in mg_props.__annotations__:
            prop_save[prop] = getattr(mg_props, prop)

        mg_props.maze_columns = mg_props.maze_rows = 10

        obj_cells = mg_props.objects.cells
        current_x = 0
        current_y = 0

        attributes = [
            (
                mg_props,
                'maze_algorithm',
                algorithm_manager.ALGORITHMS_NAMES,
                11, 11,
            ),
            (
                mg_props,
                'cell_type',
                (cells.HEXAGON, cells.POLAR, cells.SQUARE, cells.TRIANGLE),
                20, 17,
            ),
            (
                obj_cells.modifiers["MG_MASK_STAIRS"],
                'threshold',
                np.arange(0.1, 1.1, 0.1),
                11, 15,
            ),
            (
                mg_props,
                'seed',
                range(int(time.time()), int(time.time()) + 10),
                11, 11,
            ),
            (
                mg_props,
                'keep_dead_ends',
                np.arange(0, 100, 10),
                11, 11,
            ),
            (
                mg_props,
                'sparse_dead_ends',
                np.arange(1, 100, 10),
                11, 11,
            ),
            (
                obj_cells.modifiers["MG_STAIRS"],
                'strength',
                range(0, 20, 2),
                11, 11,
            ),
            (
                obj_cells.modifiers["MG_TEX_DISP"],
                'strength',
                range(-25, 25, 5),
                11, 11,
            ),
            (
                mg_props,
                'cell_inset',
                np.arange(0.0, 0.7, 0.07),
                11, 11,
            ),
            (
                obj_cells.modifiers["MG_THICK_DISP"],
                'strength',
                range(-10, 10, 2),
                11, 11,
            ),
        ]

        # dg = bpy.context.evaluated_depsgraph_get()  # Get the dependency graph
        start_time = time.time()
        for obj_from, attr, values, dx, dy in attributes[0:2]:
            current_y += dy
            start_value = getattr(obj_from, attr)
            for step_value in values:
                current_x += dx
                setattr(obj_from, attr, step_value)
                for obj in (mg_props.objects.cells, mg_props.objects.walls):
                    obj.select_set(True)
                    bpy.ops.object.duplicate()
                    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

                    # DG.update()
                    # ob = someOb.evaluated_get(DG)
                    # someMesh = bpy.data.meshes.new_from_object(ob, depsgraph=DG)

                    # obj_with_modifiers = bpy.context.object.evaluated_get(dg)  # This gives us the evaluated version of the object. Aka with all modifiers and deformations applied.

                    # mesh = obj_with_modifiers.to_mesh()  # Turn it into the mesh data block we want
                    # obj_with_modifiers.data = mesh

                    bpy.ops.object.convert(target='MESH')
                    bpy.context.object.location = (current_x, current_y, 0)
                    # bpy.context.object.data = mesh
                    bpy.ops.object.select_all(action='DESELECT')
            setattr(obj_from, attr, start_value)

            current_x = 0

        print(time.time() - start_time)

        # for prop, value in prop_save.items():
        #     exec(f'mg_props.{prop} = value')
        # setattr(mg_props, prop, value)
        # for attr in dir(mg_props):
        #     try:
        #         print(attr)
        #         print(type(getattr(mg_props, attr)).__bases__)
        #     except:
        #         pass
        # print(mg_props.__annotations__)
        # for attr in mg_props.bl_rna:
        #     print(attr)
        # columns_start = mg_props.maze_columns
        # columns_start = mg_props.maze_columns