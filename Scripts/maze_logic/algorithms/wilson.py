from random import choice
from . maze_algorithm import MazeAlgorithm


class Wilson(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1):
        super().__init__(_seed=_seed, _max_steps=_max_steps)

        unvisited = grid.get_unmasked_cells().copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0 and not self.must_break():
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited and not self.must_break():
                cell = choice([c for c in cell.get_neighbors() if c != path[-1]])
                try:
                    path = path[0:path.index(cell) + 1]
                except ValueError:
                    path.append(cell)
                self.next_step()

            for i in range(0, len(path) - 1):
                path[i].link(path[i + 1])
                path[i].group = 1
                path[i + 1].group = 1
                unvisited.remove(path[i])
            self.next_step()
