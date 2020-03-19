from random import choice
from random import seed


class RecursiveBacktracker:
    def __init__(self, grid, _seed, _max_steps=-1):
        max_steps = 100000 if _max_steps < 0 else _max_steps
        seed(_seed)

        steps = 0
        expeditions = 1

        stack = [grid.random_cell(_seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        while len(stack) > 0 and steps < max_steps:
            current = stack[-1]
            neighbors = current.get_unlinked_neighbors()
            try:

                unlinked_neighbor = choice(neighbors)
                current.link(unlinked_neighbor)
                steps += 1
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
