from random import choice
from . maze_algorithm import MazeAlgorithm


class RecursiveBacktracker(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps)
        expeditions = 1

        stack = [grid.random_cell(_seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        while len(stack) > 0 and not self.must_break():
            current = stack[-1]
            neighbors = current.get_unlinked_neighbors()
            try:
                unlinked_neighbor = choice(neighbors)
                current.link(unlinked_neighbor)
                self.next_step()
                stack.append(unlinked_neighbor)
                unlinked_neighbor.group = expeditions + 1
                backtracking = False
            except IndexError:  # No unvisited neighbor.
                stack.pop()
                if backtracking:
                    current.group = - 1
                else:
                    expeditions += 1
                backtracking = True
                pass
