"""
Octogonal Grid
"""


from .grid import (
    Grid,
    Cell,
    Vector,
)


class GridOctogon(Grid):
    """
    Octogonal Grid
    """

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            size = self.cell_size * 2
            if (row + column) % 2 == 0:
                new_cell = Cell(row, column, level, corners=8, half_neighbors=(0, 1, 2, 3))
                center = Vector((column + level * (self.columns + 1), row, 0)) * 2
                new_cell.first_vert_index = len(self.verts)

                s_q = size * 0.25
                s_tq = size * 0.75
                self.verts.extend(
                    (
                        Vector((s_q, s_tq, 0)) + center,
                        Vector((-s_q, s_tq, 0)) + center,
                        Vector((-s_tq, s_q, 0)) + center,
                        Vector((-s_tq, -s_q, 0)) + center,
                        Vector((-s_q, -s_tq, 0)) + center,
                        Vector((s_q, -s_tq, 0)) + center,
                        Vector((s_tq, -s_q, 0)) + center,
                        Vector((s_tq, s_q, 0)) + center,
                    )
                )
            else:
                new_cell = Cell(row, column, level, corners=4, half_neighbors=(0, 1))
                center = Vector((column + level * (self.columns + 1), row, 0)) * 2

                new_cell.first_vert_index = len(self.verts)
                self.verts.extend(
                    (
                        center + Vector(((size / 4), (size / 4), 0)),
                        center + Vector(((-size / 4), (size / 4), 0)),
                        center + Vector(((-size / 4), (-size / 4), 0)),
                        center + Vector(((size / 4), (-size / 4), 0)),
                    )
                )
            return new_cell

    def _get_offset(self):
        return super()._get_offset() * 2

    def init_cells_neighbors(self) -> None:
        for c in self.all_cells:
            if (c.row + c.column) % 2 == 0:
                c.set_neighbor(0, self.delta_cell(c, 0, 1, 0), 2)
                c.set_neighbor(7, self.delta_cell(c, 1, 1, 0), 3)
                c.set_neighbor(6, self.delta_cell(c, 1, 0, 0), 1)
                c.set_neighbor(5, self.delta_cell(c, 1, -1, 0), 1)
            else:
                c.set_neighbor(0, self.delta_cell(c, 0, 1, 0), 4)
                c.set_neighbor(3, self.delta_cell(c, 1, 0, 0), 2)
