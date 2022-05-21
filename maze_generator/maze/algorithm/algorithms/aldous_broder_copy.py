from .maze_algorithm import MazeAlgorithm


class AldousBroderCopy(MazeAlgorithm):
    name = "Aldous-Broder Copy"
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        expeditions = 1
        current = grid.random_cell(self._seed)
        # current.group = expeditions
        unvisited = grid.size - 1 - grid.masked_cells

        while unvisited > 0:
            neighbor = grid.get_random_neighbor(current)

            if grid.has_any_link(neighbor):
                if not grid.are_linked(current, neighbor):
                    grid.forget_neighbors(current, neighbor)
            else:
                grid.link(current, neighbor)
                unvisited -= 1
            current = neighbor
            # current.group = expeditions
