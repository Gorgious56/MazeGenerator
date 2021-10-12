from maze_generator.blender.object.cells import drivers as cells
from maze_generator.blender.object.walls import drivers as walls
from maze_generator.blender.object.helpers import drivers as helpers


def setup_drivers(scene, props):
    cells.setup_drivers(scene, props)
    walls.setup_drivers(scene, props)
    helpers.setup_drivers(scene, props)
