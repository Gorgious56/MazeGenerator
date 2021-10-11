"""
Driver Manager
"""


from .objects import cells
from .objects import walls
from .objects import helpers


def setup_drivers(scene, props):
    cells.setup_drivers(scene, props)
    walls.setup_drivers(scene, props)
    helpers.setup_drivers(scene, props)
