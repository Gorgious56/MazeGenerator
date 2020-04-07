from mathutils import Vector
from .. grids . grid import Grid
from .. cell import CellHex


class GridHex(Grid):
    def __init__(self, rows, columns, levels, cell_size, space_rep, mask=None):
        super().__init__(rows, columns, levels, cell_size, space_rep, mask, sides=6)
        self.offset = Vector((-self.columns / 3 - self.columns / 2, 1 - self.rows * (3 ** 0.5) / 2, 0))
        # self.number_of_sides = 6
        self.relative_positions_inset = self.get_relative_positions(self.cell_size)
        self.relative_positions_one = self.get_relative_positions(1)
        self.relative_positions_out = self.get_relative_positions_out()

    def prepare_grid(self):
        for r in range(self.rows):
            for c in range(self.columns):
                self[c, r] = CellHex(r, c)

    def configure_cells(self):
        for c in self.each_cell():
            row, col = c.row, c.column

            if col % 2 == 0:
                north_diagonal = row + 1
                south_diagonal = row
            else:
                north_diagonal = row
                south_diagonal = row - 1

            # Neighbor 0 : NE
            c.neighbors[0] = self[col + 1, north_diagonal]
            # Neighbor 1 : N
            c.neighbors[1] = self[col, row + 1]
            # Neighbor 2 : NW
            c.neighbors[2] = self[col - 1, north_diagonal]
            # Neighbor 3 : SW
            c.neighbors[3] = self[col - 1, south_diagonal]
            # Neighbor 4 : S
            c.neighbors[4] = self[col, row - 1]
            # Neighbor 5 : SE
            c.neighbors[5] = self[col + 1, south_diagonal]

    def get_relative_positions(self, size):
        a_size = size / 2
        b_size = size * (3 ** 0.5) / 2

        east = Vector((size, 0, 0))
        north_east = Vector((a_size, b_size, 0))
        north_west = Vector((-a_size, b_size, 0))
        west = Vector((- size, 0, 0))
        south_west = Vector((-a_size, -b_size, 0))
        south_east = Vector((a_size, -b_size, 0))
        return east, north_east, north_west, west, south_west, south_east

    def get_cell_center(self, c):
        return Vector([1 + 3 * c.column / 2, - (3 ** 0.5) * ((1 + c.column % 2) / 2 - c.row), 0]) + self.offset
