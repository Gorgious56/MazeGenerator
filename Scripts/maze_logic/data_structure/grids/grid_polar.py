from random import choice, seed
from math import pi, floor, cos, sin
from mathutils import Vector
from .. cells . cell_polar import CellPolar
from .. grids . grid import Grid


class GridPolar(Grid):
    def __init__(self, rows, columns, name="", cell_size=1):
        self.cell_size = max(0, cell_size)
        self.rows_polar = []
        self.doubling_rows = []
        super().__init__(rows, 1, name, 'polar', 4, cell_size=cell_size)

    def prepare_grid(self):
        rows = [None] * self.rows
        row_height = 1 / self.rows
        rows[0] = [CellPolar(0, 0)]

        for r in range(1, self.rows):
            radius = r / self.rows
            circumference = 2 * pi * radius

            previous_count = len(rows[r - 1])
            estimated_cell_width = circumference / previous_count
            ratio = round(estimated_cell_width / row_height + self.cell_size - 1)

            cells = previous_count * ratio
            if cells != previous_count:
                self.doubling_rows.append(r - 1)
            rows[r] = [CellPolar(r, col) for col in range(cells)]
        self.rows_polar = rows

    def __delitem__(self, key):
        del self[key[0], key[1]]

    def __getitem__(self, key):
        try:
            return self.rows_polar[key[0]][key[1]]
        except IndexError:
            return None

    def __setitem__(self, key, value):
        try:
            self.rows_polar[key[0]][key[1]] = value
        except IndexError:
            pass

    def each_row(self):
        for r in self.rows_polar:
            yield r

    def each_cell(self):
        for r in self.each_row():
            for c in r:
                if c and not c.is_masked:
                    yield c

    def get_unmasked_cells(self):  # Legacy.
        return [c for c in self.each_cell()]

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            seed(_seed)
        return choice([c for c in choice(self.rows_polar) if not c.is_masked])

    def configure_cells(self):
        # 0>cw - 1>ccw - 2>inward - 3>outward
        for c in self.each_cell():
            row, col = c.row, c.column
            if row > 0:
                c.ccw = self[row, (col + 1) % len(self.rows_polar[row])]
                c.cw = self[row, col - 1]

                ratio = len(self.rows_polar[row]) / len(self.rows_polar[row - 1])
                parent = self[row - 1, floor(col // ratio)]
                parent.outward.append(c)

                c.inward = parent

    def get_blueprint(self):
        walls, cells = [], []
        for r in self.each_row():
            for c in r:
                _, C, D, B, A = self.get_cell_position(c, len(r), self.cell_size)

                if not c.has_any_link():
                    if c.inward and c.inward.has_any_link():
                        walls.append(A)
                        walls.append(C)
                    if c.ccw and c.ccw.has_any_link():
                        walls.append(C)
                        walls.append(D)
                else:
                    if c.row > 0:
                        if not c.exists_and_is_linked(c.inward):
                            walls.append(A)
                            walls.append(C)
                        if not c.exists_and_is_linked(c.ccw):
                            walls.append(C)
                            walls.append(D)
                        if c.row == self.rows - 1:
                            walls.append(B)
                            walls.append(D)
                    if c.row >= min(self.rows - 1, 12) or c.row not in self.doubling_rows:
                        cells.append(A)
                        cells.append(B)
                        cells.append(D)
                        cells.append(C)
                    elif c.row > 0:
                        cells.append(A)
                        cells.append(B + (B - A) * (0.1 if c.row > 1 else 0.35) - Vector([0, 0, 0.01]))
                        cells.append(D + (D - C) * (0.1 if c.row > 1 else 0.35) - Vector([0, 0, 0.01]))
                        cells.append(C)
                    else:
                        cells.append(Vector([-1, 1, -0.02]))
                        cells.append(Vector([1, 1, -0.02]))
                        cells.append(Vector([1, -1, -0.02]))
                        cells.append(Vector([-1, -1, -0.02]))

        return walls, cells

    def get_cell_position(self, c, row_length, cell_size):
        t = 2 * pi / row_length
        r_in = (c.row) * cell_size
        r_out = (c.row + 1) * cell_size
        t_cw = (c.column + 1) * t
        t_ccw = c.column * t

        A = Vector([r_in * cos(t_ccw), r_in * sin(t_ccw), 0])
        B = Vector([r_out * cos(t_ccw), r_out * sin(t_ccw), 0])
        C = Vector([r_in * cos(t_cw), r_in * sin(t_cw), 0])
        D = Vector([r_out * cos(t_cw), r_out * sin(t_cw), 0])

        center = (A + B + C + D) / 4

        return center, C, D, B, A
