"""
Wrapper module to handle material creation
"""


from . import cells
from . import walls


def create_materials(props, obj_cells, obj_walls):
    cells.set_cell_materials(props, obj_cells)
    walls.set_wall_material(props, obj_walls)
