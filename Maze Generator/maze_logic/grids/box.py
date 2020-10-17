"""
Box grid
"""


from .grid import Grid, cst


class GridBox(Grid):
    """
    Box grid
    """
    def init_cells_neighbors(self) -> None:
        rows = int(self.rows / 3)
        cols = int(self.columns / 2 - rows)
        for c in self.all_cells:
            row, col, level = c.row, c.column, c.level
            # North :
            if row == 2 * rows - 1:
                if col < rows:
                    c.set_neighbor(
                        cst.NORTH, self[rows, 3 * rows - col - 1, level], cst.SOUTH)
                    c.neighbor(cst.NORTH).set_neighbor(
                        cst.WEST, c, cst.EAST)
                elif rows + cols <= col < 2 * rows + cols:
                    c.set_neighbor(
                        cst.NORTH, self[rows + cols - 1, rows - cols + col, level], cst.SOUTH)
                    c.neighbor(cst.NORTH).set_neighbor(
                        cst.EAST, c, cst.SOUTH)
                elif col >= 2 * rows + cols:
                    c.set_neighbor(
                        cst.NORTH, self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level], cst.SOUTH)
                    c.neighbor(cst.NORTH).set_neighbor(
                        cst.NORTH, c, cst.SOUTH)
                else:
                    c.set_neighbor(
                        cst.NORTH, self[col, row + 1, level], cst.SOUTH)
                    c.neighbor(cst.NORTH).set_neighbor(
                        cst.SOUTH, c, cst.NORTH)
            elif not c.neighbor(cst.NORTH):
                c.set_neighbor(
                    cst.NORTH, self[col, row + 1, level], cst.SOUTH)
                if c.neighbor(cst.NORTH):
                    c.neighbor(cst.NORTH).set_neighbor(
                        cst.SOUTH, c, cst.NORTH)
            # West :
            if not c.neighbor(cst.WEST):
                c.set_neighbor(
                    cst.WEST, self[col - 1, row, level], cst.EAST)
                if c.neighbor(cst.WEST):
                    c.neighbor(cst.WEST).set_neighbor(
                        cst.EAST, c, cst.WEST)
            # South :
            if row == rows:
                if col < rows:
                    c.set_neighbor(
                        cst.SOUTH, self[rows, col, level], cst.NORTH)
                    c.neighbor(cst.SOUTH).set_neighbor(
                        cst.WEST, c, cst.EAST)
                elif rows + cols <= col < 2 * rows + cols:
                    c.set_neighbor(
                        cst.SOUTH, self[rows + cols - 1, 2 * rows + cols - 1 - col, level], cst.NORTH)
                    c.neighbor(cst.SOUTH).set_neighbor(
                        cst.EAST, c, cst.WEST)
                elif col >= 2 * rows + cols:
                    c.set_neighbor(
                        cst.SOUTH, self[3 * rows + 2 * cols - 1 - col, 0, level], cst.NORTH)
                    c.neighbor(cst.SOUTH).set_neighbor(
                        cst.SOUTH, c, cst.NORTH)
                else:
                    c.set_neighbor(
                        cst.SOUTH, self[col, row - 1, level], cst.NORTH)
                    c.neighbor(cst.SOUTH).set_neighbor(
                        cst.NORTH, c, cst.SOUTH)
