from random import choice, seed


class Wilson:
    def __init__(self, grid, _seed, _max_steps=-1):
        steps = 100000 if _max_steps < 0 else _max_steps
        if _seed:
            seed(_seed)

        unvisited = grid.get_unmasked_cells().copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0 and steps > 0:
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited and steps > 0:
                cell = choice([c for c in cell.get_neighbors() if c != path[-1]])
                try:
                    path = path[0:path.index(cell)+1]
                except ValueError:
                    path.append(cell)
                steps -= 1

            for i in range(0, len(path)-1):
                path[i].link(path[i+1])
                path[i].group = 1
                path[i+1].group = 1
                unvisited.remove(path[i])
            steps -= 1
