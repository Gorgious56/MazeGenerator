from random import choice, seed


class AldousBroder:
    def __init__(self, grid, _seed, _max_steps=-1):
        steps = 10000 if _max_steps < 0 else _max_steps
        if _seed:
            seed(_seed)

        expeditions = 1
        current = grid.random_cell(_seed, True)
        current.group = expeditions

        unvisited = grid.size - 1 - len(grid.masked_cells)
        while unvisited > 0 and steps > 0:

            neighbor = choice(current.get_neighbors())

            if len(neighbor.links) <= 0:
                current.link(neighbor)
                unvisited -= 1
                steps -= 1
            current = neighbor
            current.group = expeditions
