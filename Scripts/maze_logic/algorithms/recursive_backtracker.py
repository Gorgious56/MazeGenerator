from . maze_algorithm import MazeAlgorithm


class RecursiveBacktracker(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=0, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        expeditions = 1

        stack = [grid.random_cell(_seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        # unlinked_neighbor = None
        direction = - 1

        while len(stack) > 0 and not self.must_break():
            current = stack[-1]

            unlinked_neighbor, direction = current.get_biased_unmasked_unlinked_directional_neighbor(bias, direction)
            if unlinked_neighbor:
                current.link(unlinked_neighbor)
                self.next_step()
                stack.append(unlinked_neighbor)
                unlinked_neighbor.group = expeditions + 1
                backtracking = False
            else:
                stack.pop()
                if backtracking:
                    current.group = - 1
                else:
                    expeditions += 1
                backtracking = True
