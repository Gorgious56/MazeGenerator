"""
Polar Grid
"""
import random
from typing import List, Generator
from math import pi, floor, cos, sin
from .grid import (
    Grid,
    cst,
    Cell,
    Vector,
)


class GridPolar(Grid):
    """
    Polar Grid
    """

    def __init__(self, rows, columns, levels, cell_size=1, branch_polar=1, *args, **kwargs):
        # self.rows_polar = []
        cell_size = max(0, cell_size)
        super().__init__(rows=rows, columns=0, levels=levels, cell_size=cell_size, init_cells=False, *args, **kwargs)

        self.doubling_rows = []
        self._cells = [None]
        self.row_begin_index = [0]

        row_height = 1 / self.rows
        self.branch = branch_polar

        for r in range(1, self.rows):
            self.row_begin_index.append(len(self._cells))
            radius = r / self.rows
            circumference = 2 * pi * radius

            previous_columns = self.row_begin_index[-1] - self.row_begin_index[-2]

            # Prev count * ratio. Place multiplier here
            columns = previous_columns * round(circumference * self.branch / previous_columns / row_height)
            if columns != previous_columns:
                self.doubling_rows.append(r - 1)
            self._cells.extend([None] * columns)

    def __delitem__(self, key):
        del self[key[0], key[1]]

    def __getitem__(self, key):
        key = list(key)
        if 0 <= key[1] < self.rows:
            if key[1] == self.rows - 1:
                row = self._cells[self.row_begin_index[key[1]] : :]
            else:
                row = self._cells[self.row_begin_index[key[1]] : self.row_begin_index[key[1] + 1]]
            if key[0] == len(row):
                key[0] = 0
            elif key[0] == -1:
                key[0] = len(row) - 1
            return row[key[0]]

    def __setitem__(self, key, value):
        key = list(key)
        if 0 <= key[1] < self.rows:
            if key[1] == self.rows - 1:
                row = self._cells[self.row_begin_index[key[1]] : :]
            else:
                row = self._cells[self.row_begin_index[key[1]] : self.row_begin_index[key[1] + 1]]
            if key[0] == len(row):
                key[0] = 0
            elif key[0] == -1:
                key[0] = len(row) - 1
            self._cells[self.row_begin_index[key[1]] + key[0]] = value

    def delta_cell(self, cell: Cell, column: int = 0, row: int = 0, level: int = 0) -> Cell:
        if not cell:
            return
        if column == -1:
            if cell.row == 0:
                return random.choice(cell.neighbors)
            else:
                return self[cell.column - 1, cell.row]
        elif column == 1:
            if cell.row == 0:
                return random.choice(cell.neighbors)
            else:
                return self[cell.column + 1, cell.row]
        elif row == -1:
            if cell.row > 0:
                return cell.neighbor(1)
        elif row == 1:
            if cell.row == 0:
                return random.choice(cell.neighbors)
            else:
                outward_neighbors = [c for c in cell._neighbors[3::] if c]
                return random.choice(outward_neighbors) if outward_neighbors else None

    def get_columns_this_row(self, row):
        return (
            self.row_begin_index[row + 1] - self.row_begin_index[row]
            if row < self.rows - 1
            else len(self._cells) - self.row_begin_index[row]
        )

    def prepare_grid(self) -> None:
        for l in range(self.levels):
            for r in range(self.rows):
                for c in range(self.get_columns_this_row(r)):
                    new_cell = self.create_cell(r, c, l)
                    self[c, r, l] = new_cell

    def init_cells_neighbors(self) -> None:
        # 0>ccw - 1>in - 2>cw - 3...>outward
        all_cells = self.all_cells
        for c in all_cells:
            row, col = c.row, c.column
            if row > 0:
                row_length = self.get_columns_this_row(c.row)
                c.set_neighbor(0, self.delta_cell(c, column=1), 2)

                ratio = row_length / self.get_columns_this_row(c.row - 1)
                inward = self[floor(col // ratio), row - 1]
                c.set_neighbor(cst.POL_IN, inward, add_as_new=True)

        for cell in all_cells:
            cell.first_vert_index = len(self.verts)
            self.verts.extend(self.get_cell_positions(cell))
            self.new_cell_evt(cell)

    def each_row(self) -> Generator[List[Cell], None, None]:
        """
        Travel the grid row by row, starting at index 0
        """
        for i in range(len(self.row_begin_index)):
            if i < self.rows - 1:
                yield self._cells[self.row_begin_index[i] : self.row_begin_index[i + 1]]
            else:
                yield self._cells[self.row_begin_index[i] : :]

    def get_position(self, radius, angle):
        return Vector((radius * cos(angle), radius * sin(angle), 0))

    def get_cell_positions(self, cell):
        cs = self.cell_size
        if cell.row == 0:
            t = 0
            corners = self.get_columns_this_row(1)
            dt = 2 * pi / corners
            positions = []
            for c in range(corners):
                positions.append(self.get_position(cs, t))
                t += dt
            return positions

        row_length = self.get_columns_this_row(cell.row)
        t = 2 * pi / row_length
        r_in = cell.row + 0.5 - cs / 2
        r_out = r_in + cs
        t_cw = (cell.column + 0.5 - cs / 2) * t
        t_ccw = t_cw + cs * t

        r_in_cw = self.get_position(r_in, t_cw)
        r_out_cw = self.get_position(r_out, t_cw)
        r_in_ccw = self.get_position(r_in, t_ccw)
        r_out_ccw = self.get_position(r_out, t_ccw)
        if cell.corners == 5:
            return (
                r_out_ccw,
                r_in_ccw,
                r_in_cw,
                r_out_cw,
                self.get_position(r_out, (2 * cell.column + 1) * 2 * pi / self.get_columns_this_row(cell.row + 1)),
            )
        else:
            return (r_out_ccw, r_in_ccw, r_in_cw, r_out_cw)

    def _get_offset(self) -> Vector:
        return Vector((0, 0, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            if row == 0:
                new_cell = Cell(row, column, level, corners=0, half_neighbors=[])
            else:
                new_cell = Cell(row, column, level, corners=4, half_neighbors=(0, 1))
            return new_cell

    def get_outer_cells(self):
        last_row = self.rows - 1
        cols_this_row = self.get_columns_this_row(last_row)
        start_cell = self[random.randint(0, cols_this_row), self.rows - 1]
        end_cell = self[int(start_cell.column + cols_this_row / 2) % cols_this_row, self.rows - 1]
        print(start_cell, end_cell)
        return start_cell, end_cell
