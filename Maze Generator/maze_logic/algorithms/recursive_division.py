from random import randrange
from .maze_algorithm import MazeAlgorithm
from ...utils import methods

class RecursiveDivision(MazeAlgorithm):
    name = 'Recursive Division'
    weaved = False
    settings = ['maze_bias']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        self.divide(0, 0, self.grid.rows, self.grid.columns)

    def divide(self, mx, my, ax, ay):
        HORIZONTAL, VERTICAL = 0, 1
        grid = self.grid

        dx = ax - mx
        dy = ay - my
        if dx < 2 or dy < 2:
            # make a hallway
            if dx > 1:
                y = my
                for x in range(mx, ax):
                    self.link(grid[y, x], 2)
            elif dy > 1:
                x = mx
                for y in range(my, ay):
                    self.link(grid[y, x], 3)
            return

        wall = HORIZONTAL if dy > dx else (VERTICAL if dx > dy else randrange(2))

        xp = methods.get_biased_choices(list(range(mx, ax - (wall == VERTICAL))), self.bias)[0]
        yp = methods.get_biased_choices(list(range(my, ay - (wall == HORIZONTAL))), self.bias)[0]

        if wall == HORIZONTAL:
            nx, ny = ax, yp + 1
            neighbor = 3
            ox, oy = mx, ny
        else:
            nx, ny = xp + 1, ay
            neighbor = 2
            ox, oy = nx, my
        self.link(grid[yp, xp], neighbor)

        self.divide(mx, my, nx, ny)
        self.divide(ox, oy, ax, ay)

    def link(self, cell, neighbor_number):
        if cell:
            n = cell.neighbor(neighbor_number)
            if n and not self.grid.connected(cell, n):
                self.grid.link(cell, n)
                return True
        return False
