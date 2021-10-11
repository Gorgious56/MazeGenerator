"""
Dodecagon grid
"""


from .grid import (
    Grid,
    Cell,
    Vector,
)


class GridDodecagon(Grid):
    """
    Dodecagon grid
    """

    def _get_offset(self) -> Vector:
        return Vector((-0.5 - self.columns, -(self.rows // 3) * 7 / 8, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            size = self.cell_size * 2
            if row % 3 == 0:  # Up triangle
                new_cell = Cell(row, column, level, corners=3, half_neighbors=(1,))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 7 / 4 * (row / 3) + 1 / 4, 0))
                new_cell.first_vert_index = len(self.verts)
                self.verts.extend(
                    (
                        Vector((size / 8, 0, 0)) + center,
                        Vector((0, size / 4, 0)) + center,
                        Vector((-size / 8, 0, 0)) + center,
                    )
                )
            elif (row - 2) % 3 == 0:  # Down trianlge
                new_cell = Cell(row, column, level, corners=3, half_neighbors=(0, 2))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 7 / 4 * (((row - 2) / 3) + 1), 0))
                new_cell.first_vert_index = len(self.verts)
                self.verts.extend(
                    (
                        Vector((-size / 8, 0, 0)) + center,
                        Vector((0, -size / 4, 0)) + center,
                        Vector((size / 8, 0, 0)) + center,
                    )
                )
            else:
                new_cell = Cell(row, column, level, corners=12, half_neighbors=(0, 1, 2, 3, 4, 5))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 1 + ((row - 1) * 7 / 4 / 3), 0))
                new_cell.first_vert_index = len(self.verts)
                s_q = size * 0.25 / 2
                s_h = size / 2
                s_tq = size * 0.75 / 2

                self.verts.extend(
                    (
                        Vector((s_tq, s_tq, 0)) + center,
                        Vector((s_q, s_h, 0)) + center,
                        Vector((-s_q, s_h, 0)) + center,
                        Vector((-s_tq, s_tq, 0)) + center,
                        Vector((-s_h, s_q, 0)) + center,
                        Vector((-s_h, -s_q, 0)) + center,
                        Vector((-s_tq, -s_tq, 0)) + center,
                        Vector((-s_q, -s_h, 0)) + center,
                        Vector((s_q, -s_h, 0)) + center,
                        Vector((s_tq, -s_tq, 0)) + center,
                        Vector((s_h, -s_q, 0)) + center,
                        Vector((s_h, s_q, 0)) + center,
                    )
                )
            return new_cell

    def init_cells_neighbors(self) -> None:
        for c in self.all_cells:
            if (c.row - 1) % 3 == 0:
                c.set_neighbor(1, self.delta_cell(c, 0, 2, 0), 2)
                c.set_neighbor(7, self.delta_cell(c, 0, -2, 0), 2)
                c.set_neighbor(4, self.delta_cell(c, -1, 0, 0), 10)
                if (c.row - 1) % 2 == 0:
                    c.set_neighbor(0, self.delta_cell(c, 0, 3, 0), 6)
                    c.set_neighbor(2, self.delta_cell(c, -1, 3, 0), 8)
                    c.set_neighbor(3, self.delta_cell(c, -1, 1, 0), 1)
                    c.set_neighbor(5, self.delta_cell(c, -1, -1, 0), 0)
                    c.set_neighbor(9, self.delta_cell(c, 0, -1, 0), 1)
                    c.set_neighbor(11, self.delta_cell(c, 0, 1, 0), 0)
                else:
                    c.set_neighbor(0, self.delta_cell(c, 1, 3, 0), 6)
                    c.set_neighbor(2, self.delta_cell(c, 0, 3, 0), 8)
                    c.set_neighbor(3, self.delta_cell(c, 0, 1, 0), 1)
                    c.set_neighbor(5, self.delta_cell(c, 0, -1, 0), 0)
                    c.set_neighbor(9, self.delta_cell(c, 1, -1, 0), 1)
                    c.set_neighbor(11, self.delta_cell(c, 1, 1, 0), 0)
