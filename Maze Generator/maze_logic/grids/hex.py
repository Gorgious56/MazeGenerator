"""
Hexagonal Grid
"""


from mathutils import Vector
from ..cells import Cell
from .grid import Grid


class GridHex(Grid):
    """
    Hexagonal Grid
    """

    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            row, col = c.row, c.column
            north_diagonal = row + (1 if col % 2 == 0 else 0)
            # Neighbor 0 : NE
            c.set_neighbor(0, self[col + 1, north_diagonal], 3)
            # Neighbor 1 : N
            c.set_neighbor(1, self[col, row + 1], 4)
            # Neighbor 2 : NW
            c.set_neighbor(2, self[col - 1, north_diagonal], 5)

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 3 - self.columns / 2, 1 - self.rows * (3 ** 0.5) / 2, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            new_cell = Cell(
                row, column, level,
                corners=6,
                half_neighbors=(0, 1, 2))

            center = Vector((1 + 3 * column / 2, - (3 ** 0.5)
                             * ((1 + column % 2) / 2 - row), 0))
            size = self.cell_size
            new_cell.first_vert_index = len(self.verts)
            a_size = size / 2
            b_size = size * (3 ** 0.5) / 2

            east = Vector((size, 0, 0)) + center
            north_east = Vector((a_size, b_size, 0)) + center
            north_west = Vector((-a_size, b_size, 0)) + center
            west = Vector((- size, 0, 0)) + center
            south_west = Vector((-a_size, -b_size, 0)) + center
            south_east = Vector((a_size, -b_size, 0)) + center
            self.verts.extend((east, north_east, north_west,
                               west, south_west, south_east))
            return new_cell
