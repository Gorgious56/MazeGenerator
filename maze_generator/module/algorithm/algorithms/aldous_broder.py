from random import choice
from .maze_algorithm import MazeAlgorithm


class AldousBroder(MazeAlgorithm):
    name = "Aldous-Broder"
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        expeditions = 1
        current = grid.random_cell(self._seed)
        current.group = expeditions

        unvisited = grid.size - 1 - grid.masked_cells
        while unvisited > 0:

            neighbor = choice(current.neighbors)

            if not neighbor.has_any_link():
                grid.link(current, neighbor)
                unvisited -= 1
            current = neighbor
            current.group = expeditions
