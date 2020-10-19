"""
Wrapper module to handle material creation
"""


from . import cells
from . import walls


def create_materials(props):
    cells.set_cell_materials(props)
    walls.set_wall_material(props)
