"""
Handle material creation
"""

from . import cells
from . import walls

def update_links(props):
    cells.update_links(props)

def create_materials(scene, props):
    cells.set_cell_materials(scene, props)
    walls.set_wall_material(props)
