from random import choice
from . maze_algorithm import MazeAlgorithm


class AldousBroder(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, close_chance=1):
        super().__init__(_seed=_seed, _max_steps=_max_steps)

        expeditions = 1
        current = grid.random_cell(_seed, True)
        current.group = expeditions

        unvisited = grid.size - 1 - len(grid.masked_cells)
        while unvisited > 0 and not self.must_break():

            neighbor = choice(current.get_neighbors())

            if len(neighbor.links) <= 0:
                current.link(neighbor)
                unvisited -= 1
                self.next_step()
            current = neighbor
            current.group = expeditions
