"""
Triangle Grid
"""


from mathutils import Vector
from .grid import (
    Grid,
    Cell,
    cst,
)


class GridTriangle(Grid):
    """
    Triangle Grid
    """

    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            if (c.row + c.column) % 2 == 0:
                c.set_neighbor(0, self.delta_cell(c, column=1), 0)
                c.set_neighbor(1, self.delta_cell(c, column=-1), 1)
                c.set_neighbor(2, self.delta_cell(c, row=-1), 2)

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 4, -self.rows / 3, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            up_right = (row + column) % 2 == 0
            new_cell = Cell(row, column, level, corners=3, half_neighbors=(0, 1, 2) if up_right else [])

            center = Vector((column * 0.5, row * cst.SQRT3_OVER2, 0))
            size = self.cell_size
            new_cell.first_vert_index = len(self.verts)

            half_width = size / 2
            height = size * (3 ** 0.5) / 2
            half_height = height / 2

            if up_right:
                base_y = -half_height
                apex_y = half_height
                self.verts.extend(
                    (
                        Vector((half_width, base_y, 0)) + center,
                        Vector((0, apex_y, 0)) + center,
                        Vector((-half_width, base_y, 0)) + center,
                    )
                )
            else:
                base_y = half_height
                apex_y = -half_height
                self.verts.extend(
                    (
                        Vector((-half_width, base_y, 0)) + center,
                        Vector((0, apex_y, 0)) + center,
                        Vector((half_width, base_y, 0)) + center,
                    )
                )

            return new_cell
