"""
Box grid
"""


from .grid import (
    Grid,
    cst,
)


class GridBox(Grid):
    """
    Box grid
    """

    def init_cells_neighbors(self) -> None:
        rows = int(self.rows / 3)
        cols = int(self.columns / 2 - rows)
        for c in self.all_cells:
            row, col, level = c.row, c.column, c.level
            if row == 2 * rows - 1:
                if col < rows:
                    c.set_neighbor(cst.NORTH, self[rows, 3 * rows - col - 1, level], cst.WEST)
                elif rows + cols <= col < 2 * rows + cols:
                    c.set_neighbor(cst.NORTH, self[rows + cols - 1, rows - cols + col, level], cst.EAST)
                elif col >= 2 * rows + cols:
                    c.set_neighbor(cst.NORTH, self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level], cst.NORTH)
            elif row == rows:
                if col < rows:
                    c.set_neighbor(cst.SOUTH, self[rows, col, level], cst.WEST)
                elif rows + cols <= col < 2 * rows + cols:
                    # Not working. Investigate
                    c.set_neighbor(cst.SOUTH, self[rows + cols - 1, 2 * rows + cols - 1 - col, level], cst.EAST)
                elif col >= 2 * rows + cols:
                    # Not working. Investigate
                    c.set_neighbor(cst.SOUTH, self[3 * rows + 2 * cols - 1 - col, 0, level], cst.SOUTH)

            if row > 0 and (row != rows or rows < col < rows + cols):
                c.set_neighbor(cst.SOUTH, self[col, row - 1, level], cst.NORTH)
            if col > 0 and (col != rows or rows < row < 2 * rows):
                c.set_neighbor(cst.WEST, self[col - 1, row, level], cst.EAST)
