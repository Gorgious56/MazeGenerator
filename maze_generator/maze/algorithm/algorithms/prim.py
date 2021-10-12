from .maze_algorithm import (
    MazeAlgorithm,
    randrange,
    choice,
)
from maze_generator.maze.algorithm.helper.priority_queue import PriorityQueue


class Prim(MazeAlgorithm):
    name = "Prim"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bias = round((1 - abs(self.bias)) * 10)

        self.q = PriorityQueue()
        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        start_cell = self.grid.random_cell()
        self.push_to_queue(start_cell)

        while not self.q.is_empty():
            cell, neighbor = self.q.pop()
            if not self.grid.connected(cell, neighbor):
                self.grid.link(cell, neighbor)
                self.push_to_queue(neighbor)
            self.push_to_queue(cell)

    def push_to_queue(self, cell):
        try:
            self.q.push((cell, choice(cell.get_unlinked_neighbors())), randrange(0, self.bias + 1))
        except IndexError:
            pass
