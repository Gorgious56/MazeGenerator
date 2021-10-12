"""
Handle material creation
"""

from maze_generator.blender.object.cells import shading as cells
from maze_generator.blender.object.walls import shading as walls


def update_links(props):
    cells.update_links(props)


def create_materials(scene, props):
    cells.set_materials(scene, props)
    walls.set_material(props)
