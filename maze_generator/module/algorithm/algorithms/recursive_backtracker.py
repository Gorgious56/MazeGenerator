from .maze_algorithm import MazeAlgorithm


class RecursiveBacktracker(MazeAlgorithm):
    name = "Recursive Backtracker"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        expeditions = 1

        stack = [self.grid.random_cell(self._seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        direction = -1

        while len(stack) > 0:
            current = stack[-1]

            unlinked_neighbor, direction = current.get_biased_unlinked_directional_neighbor(self.bias, direction)
            if unlinked_neighbor:
                self.grid.link(current, unlinked_neighbor)
                stack.append(unlinked_neighbor)
                unlinked_neighbor.group = expeditions + 1
                backtracking = False
            else:
                stack.pop()
                if backtracking:
                    current.group = -1
                else:
                    expeditions += 1
                backtracking = True
