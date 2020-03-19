from random import choice, seed


class CrossStitch:
    def __init__(self, grid, _seed=None, _max_steps=-1):
        steps = 100000 if _max_steps < 0 else _max_steps
        if _seed:
            seed(_seed)

        current = grid.random_cell(_seed)
        current.group = 1

        while current and steps > 0:
            unvisited_neighbors = current.get_unlinked_neighbors()

            if len(unvisited_neighbors) > 0:
                neighbor = choice(unvisited_neighbors)
                current.link(neighbor)
                current = neighbor
                current.group = 1
            else:
                current = None
            steps -= 1

            for c in grid.each_cell():  # TODO optimize
                if steps <= 0:
                    break
                visited_neighbors = c.get_linked_neighbors()
                if not c.has_any_link() and len(visited_neighbors) > 0:
                    current = c
                    current.group = 1
                    neighbor = choice(visited_neighbors)
                    current.link(neighbor)
                    neighbor.group = 3
                    steps -= 1
