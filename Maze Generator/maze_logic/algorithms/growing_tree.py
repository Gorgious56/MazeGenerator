from random import choice
from .maze_algorithm import MazeAlgorithm

class GrowingTree(MazeAlgorithm):
    name = 'Growing Tree'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.run()

    def run(self):
        active_cells = [self.grid.random_cell()]

        while active_cells:
            cell = choice(list(reversed(active_cells))[0:int(len(active_cells) * self.bias) + 1])
            unlinked_neighbors = cell.get_unlinked_neighbors()
            if unlinked_neighbors:
                available_neighbor = choice(unlinked_neighbors)
                self.grid.link(cell, available_neighbor)
                active_cells.append(available_neighbor)
            else:
                active_cells.remove(cell)
