from random import choice
from . maze_algorithm import MazeAlgorithm


class CrossStitch(MazeAlgorithm):
    def __init__(self, grid, _seed=-1, _max_steps=-1):
        super().__init__(_seed=_seed, _max_steps=_max_steps)

        current = grid.random_cell(_seed)
        current.group = 1

        while current and not self.must_break():
            unvisited_neighbors = current.get_unlinked_neighbors()

            if len(unvisited_neighbors) > 0:
                neighbor = choice(unvisited_neighbors)
                current.link(neighbor)
                current = neighbor
                current.group = 1
            else:
                current = None
            self.next_step()

            for c in grid.each_cell():  # TODO optimize
                if self.must_break():
                    break
                visited_neighbors = c.get_linked_neighbors()
                if not c.has_any_link() and len(visited_neighbors) > 0:
                    current = c
                    current.group = 1
                    neighbor = choice(visited_neighbors)
                    current.link(neighbor)
                    neighbor.group = 3
                    self.next_step()
