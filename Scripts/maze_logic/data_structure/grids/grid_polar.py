from random import choice, seed
from math import pi, floor, cos, sin
from mathutils import Vector
from .. cell import CellPolar
from .. grids . grid import Grid, CellVisual

# CW_OUT = 'CW_OUT'
# CW_IN = 'CW_IN'
# CCW_IN = 'CCW_IN'
# CCW_OUT = 'CCW_OUT'
# ALL_CORNERS = 'ALL_CORNERS'
# CCW_IN_B_B = 'CCW_IN_B_IN'
# CCW_IN_B_CCW = 'CCW_IN_B_CCW'
# CCW_IN_B_IN = 'CCW_IN_B_IN'
# CCW_OUT_B_B = 'CCW_OUT_B_B'
# CCW_OUT_B_CCW = 'CCW_OUT_B_CCW'
# CCW_OUT_B_IN = 'CCW_OUT_B_IN'
# CW_IN_B_B = 'CW_IN_B_IN'
# CW_IN_B_CCW = 'CW_IN_B_CCW'
# CW_IN_B_IN = 'CW_IN_B_IN'
# CW_OUT_B_B = 'CW_OUT_B_B'
# CW_OUT_B_CCW = 'CW_OUT_B_CCW'
# CW_OUT_B_IN = 'CW_OUT_B_IN'

# R_IN = 'R_IN'
# R_OUT = 'R_OUT'
# R_IN_B = 'R_IN_B'
# R_OUT_B = 'R_OUT_B'
# T_CW = 'T_CW'
# T_CCW = 'T_CCW'
# T_CW_B = 'T_CW_B'
# T_CCW_B = 'T_CCW_B'


class GridPolar(Grid):
    def __init__(self, cell_size=1, *args, **kwargs):
        self.cell_size = max(0, cell_size)
        self.rows_polar = []
        self.doubling_rows = []
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
        rows = [None] * self.rows
        row_height = 1 / self.rows
        rows[0] = [CellPolar(0, 0)]

        for r in range(1, self.rows):
            radius = r / self.rows
            circumference = 2 * pi * radius

            previous_count = len(rows[r - 1])
            estimated_cell_width = circumference / previous_count
            ratio = round(estimated_cell_width / row_height)  # Place multiplier here

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

    def get_cell_walls(self, c):
        cv = CellVisual(c)
        row_length = len(self.rows_polar[c.row])
        cs = self.cell_size
        t = 2 * pi / row_length
        r_in = c.row
        r_out = c.row + 1
        t_ccw = (c.column + 1) * t
        t_cw = c.column * t

        if cs == 1:
            if c.row == 0:
                sqrt_3_over_2 = (3 ** 0.5) / 2
                cv.add_face((
                    Vector((-1, 0, 0)), Vector((-0.5, -sqrt_3_over_2, 0)), Vector((0.5, -sqrt_3_over_2, 0)),
                    Vector((1, 0, 0)), Vector((0.5, sqrt_3_over_2, 0)), Vector((-0.5, sqrt_3_over_2, 0))))
            else:
                if c.has_any_link():
                    if not c.exists_and_is_linked(c.inward):
                        cv.create_wall(self.get_position(r_in, t_ccw), self.get_position(r_in, t_cw))
                    if not c.exists_and_is_linked(c.ccw):
                        cv.create_wall(self.get_position(r_in, t_ccw), self.get_position(r_out, t_ccw))
                    if c.row == self.rows - 1:
                        cv.create_wall(self.get_position(r_out, t_cw), self.get_position(r_out, t_ccw))
                else:
                    if c.inward and c.inward.has_any_link():
                        cv.create_wall(self.get_position(r_in, t_ccw), self.get_position(r_in, t_cw))
                    if c.ccw and c.ccw.has_any_link():
                        cv.create_wall(self.get_position(r_in, t_cw), self.get_position(r_out, t_ccw))

                if c.row in self.doubling_rows:
                    t_over = pi / row_length
                    t_cw_over = ((c.column * 2) + 1) * t_over
                    cv.add_face((self.get_position(r_in, t_cw), self.get_position(r_in, t_ccw), self.get_position(r_out, t_ccw), self.get_position(r_out, t_cw_over), self.get_position(r_out, t_cw)))
                else:
                    cv.add_face((self.get_position(r_in, t_cw), self.get_position(r_in, t_ccw), self.get_position(r_out, t_ccw), self.get_position(r_out, t_cw)))
        else:
            r_in_b = c.row + 0.5 - cs / 2
            r_out_b = c.row + 0.5 + cs / 2
            t_ccw_b = (c.column + 0.5 + cs / 2) * t
            t_cw_b = (c.column + 0.5 - cs / 2) * t

            if c.row == 0:
                sqrt_3_over_2 = (3 ** 0.5) / 2
                cv.add_face((
                    Vector((-1, 0, 0)), Vector((-0.5, -sqrt_3_over_2, 0)), Vector((0.5, -sqrt_3_over_2, 0)),
                    Vector((1, 0, 0)), Vector((0.5, sqrt_3_over_2, 0)), Vector((-0.5, sqrt_3_over_2, 0))))
            elif c.row in self.doubling_rows:
                t_over = pi / row_length
                t_cw_over = (c.column * 2 + 1) * t_over
                t_ccw_over = (c.column * 2 + 2 - cs / 3) * t_over
                t_ccw_over_2 = (c.column * 2 + cs / 3) * t_over
                cv.add_face((self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b, t_cw_b), self.get_position(r_out_b, t_cw_over), self.get_position(r_out_b, t_ccw_b), self.get_position(r_in_b, t_ccw_b)))

                if c.exists_and_is_linked(c.inward):
                    r_inward_b = c.row - 0.5 + cs / 2
                    cv.add_face((self.get_position(r_in_b, t_ccw_b), self.get_position(r_inward_b, t_ccw_b), self.get_position(r_inward_b, t_cw_b), self.get_position(r_in_b, t_cw_b)))
                if c.exists_and_is_linked(c.ccw):
                    cv.add_face((self.get_position(r_out_b, t_ccw_b), self.get_position(r_out_b, t_ccw), self.get_position(r_in_b, t_ccw), self.get_position(r_in_b, t_ccw_b)))
                elif len(c.outward) > 1 and c.exists_and_is_linked(c.outward[1]):
                    cv.add_face((self.get_position(r_out_b, t_ccw_b), self.get_position(r_out_b, t_ccw_over), self.get_position(r_in_b, t_ccw_over), self.get_position(r_in_b, t_ccw_b)))
                if c.exists_and_is_linked(c.cw):
                    cv.add_face((self.get_position(r_in_b, t_cw_b), self.get_position(r_in_b, t_cw), self.get_position(r_out_b, t_cw), self.get_position(r_out_b, t_cw_b)))
                elif len(c.outward) > 0 and c.exists_and_is_linked(c.outward[0]):
                    cv.add_face((self.get_position(r_in_b, t_cw_b), self.get_position(r_in_b, t_ccw_over_2), self.get_position(r_out_b, t_ccw_over_2), self.get_position(r_out_b, t_cw_b)))
            else:
                cv.add_face((self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b, t_cw_b), self.get_position(r_out_b, t_ccw_b), self.get_position(r_in_b, t_ccw_b)))
                if c.exists_and_is_linked(c.inward):
                    r_inward_b = c.row - 0.5 + cs / 2
                    cv.add_face((self.get_position(r_in_b, t_ccw_b), self.get_position(r_inward_b, t_ccw_b), self.get_position(r_inward_b, t_cw_b), self.get_position(r_in_b, t_cw_b)))
                if c.exists_and_is_linked(c.ccw):
                    cv.add_face((self.get_position(r_out_b, t_ccw_b), self.get_position(r_out_b, t_ccw), self.get_position(r_in_b, t_ccw), self.get_position(r_in_b, t_ccw_b)))
                if c.exists_and_is_linked(c.cw):
                    cv.add_face((self.get_position(r_in_b, t_cw_b), self.get_position(r_in_b, t_cw), self.get_position(r_out_b, t_cw), self.get_position(r_out_b, t_cw_b)))

        return cv

    def get_unmasked_cells(self):
        return [c for c in self.each_cell() if not c.is_masked]

    def get_position(self, radius, angle):
        return Vector((radius * cos(angle), radius * sin(angle), 0))
