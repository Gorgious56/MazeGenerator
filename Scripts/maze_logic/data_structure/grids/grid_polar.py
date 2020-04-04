from random import choice, seed
from math import pi, floor, cos, sin
from mathutils import Vector
from .. cell import CellPolar
from .. grids . grid import Grid


class GridPolar(Grid):
    def __init__(self, rows, columns, levels, cell_size=1, space_rep=0, *args, **kwargs):
        self.rows_polar = []
        self.doubling_rows = []
        cell_size = max(0, cell_size)
        super().__init__(rows=rows, columns=1, levels=levels, space_rep='1', cell_size=cell_size, *args, **kwargs)

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

    def each_row(self):
        for r in self.rows_polar:
            yield r

    def each_cell(self):
        for r in self.each_row():
            for c in r:
                if c:
                    yield c

    def all_cells(self):
        cells = []
        for r in self.each_row():
            for c in r:
                if c:
                    cells.append(c)
        return cells

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            seed(_seed)
        return choice([c for c in choice(self.rows_polar)])

    def set_cell_visuals(self, c):
        # The faces are all reversed but inverting all of the calculations is a big hassle.
        # Hacky but works.
        cv = c.visual
        row_length = len(self.rows_polar[c.row])
        cs = self.cell_size
        t = 2 * pi / row_length
        r_in = c.row
        r_out = c.row + 1
        t_ccw = (c.column + 1) * t
        t_cw = c.column * t

        face_walls = []

        if cs == 1:
            if c.row == 0:
                [face_walls.extend(((2 - i % 6), (3 - i) % 6)) for i, o in enumerate(c.outward) if not c.exists_and_is_linked(o)]
                sqrt_3_over_2 = (3 ** 0.5) / 2
                cv.add_face((
                    Vector((-1, 0, 0)), Vector((-0.5, sqrt_3_over_2, 0)), Vector((0.5, sqrt_3_over_2, 0)),
                    Vector((1, 0, 0)), Vector((0.5, -sqrt_3_over_2, 0)), Vector((-0.5, -sqrt_3_over_2, 0))),
                    walls=face_walls)
            else:
                if not c.exists_and_is_linked(c.inward):
                    face_walls.extend((0, 1))
                if not c.exists_and_is_linked(c.ccw):
                    face_walls.extend((1, 2))

                if c.row in self.doubling_rows:
                    if c.row == self.rows - 1:
                        face_walls.extend((2, 3, 3, 4))
                    else:
                        [face_walls.extend((3 - i, 4 - i)) for i, o in enumerate(c.outward)if not c.exists_and_is_linked(o)]
                    if not c.exists_and_is_linked(c.cw):
                        face_walls.extend((4, 0))
                    cv.add_face(
                        (self.get_position(r_in, t_cw), self.get_position(r_in, t_ccw), self.get_position(r_out, t_ccw), self.get_position(r_out, (t_cw + t_ccw) / 2), self.get_position(r_out, t_cw)),
                        walls=face_walls)
                else:
                    if not c.exists_and_is_linked(c.cw):
                        face_walls.extend((3, 0))
                    if c.row == self.rows - 1 or not c.is_linked_outward():
                        face_walls.extend((2, 3))
                    cv.add_face(
                        (self.get_position(r_in, t_cw), self.get_position(r_in, t_ccw), self.get_position(r_out, t_ccw), self.get_position(r_out, t_cw)),
                        walls=face_walls)
        else:
            r_in_b = c.row + 0.5 - cs / 2
            r_out_b = c.row + 0.5 + cs / 2
            t_ccw_b = (c.column + 0.5 + cs / 2) * t
            t_cw_b = (c.column + 0.5 - cs / 2) * t
            if c.row == 0:
                [face_walls.extend(((2 - i % 6), (3 - i) % 6)) for i, o in enumerate(c.outward) if not c.exists_and_is_linked(o)]
                sqrt_3_over_2 = (3 ** 0.5) * cs / 2
                cv.add_face((
                    Vector((-cs, 0, 0)), Vector((-cs / 2, sqrt_3_over_2, 0)), Vector((cs / 2, sqrt_3_over_2, 0)),
                    Vector((cs, 0, 0)), Vector((cs / 2, -sqrt_3_over_2, 0)), Vector((-cs / 2, -sqrt_3_over_2, 0))),
                    walls=face_walls)
            elif c.row in self.doubling_rows:
                t_over = pi / row_length
                t_cw_over = (c.column * 2 + 1) * t_over

                if c.exists_and_is_linked(c.inward):
                    if c.row == 1:
                        r_inward_b = cs
                        cv.add_face(
                            (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_inward_b, c.column * pi / 3), self.get_position(r_inward_b, (c.column + 1) * pi / 3)),
                            walls=(0, 3, 2, 1))
                    elif c.row - 1 in self.doubling_rows:
                        c_i = c.inward
                        row_length_i = len(self.rows_polar[c_i.row])
                        t_i = 2 * pi / row_length_i
                        t_over_i = pi / row_length_i
                        t_cw_over_i = (c_i.column * 2 + 1) * t_over_i
                        r_out_b_i = c_i.row + 0.5 + cs / 2
                        t_cw_b_i = (c_i.column + 0.5 - cs / 2) * t_i
                        t_ccw_b_i = (c_i.column + 0.5 + cs / 2) * t_i
                        if c_i.outward.index(c) == 0:
                            cv.add_face(
                                (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b_i, t_cw_b_i), self.get_position(r_out_b_i, t_cw_over_i)),
                                walls=(0, 3, 2, 1))
                        else:
                            cv.add_face(
                                (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b_i, t_cw_over_i), self.get_position(r_out_b_i, t_ccw_b_i)),
                                walls=(0, 3, 2, 1))
                    else:
                        r_inward_b = c.row - 0.5 + cs / 2
                        cv.add_face(
                            (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_inward_b, t_cw_b), self.get_position(r_inward_b, t_ccw_b)),
                            walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((0, 1))

                if c.exists_and_is_linked(c.ccw):
                    cv.add_face(
                        (self.get_position(r_out_b, t_ccw_b), self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_ccw), self.get_position(r_out_b, t_ccw)),
                        walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((1, 2))

                if c.exists_and_is_linked(c.cw):
                    cv.add_face(
                        (self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b, t_cw_b), self.get_position(r_out_b, t_cw), self.get_position(r_in_b, t_cw)),
                        walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((4, 0))

                if not c.exists_and_is_linked(c.outward[0]):
                    face_walls.extend((3, 4))
                if not c.exists_and_is_linked(c.outward[1]):
                    face_walls.extend((2, 3))

                cv.add_face(
                    (self.get_position(r_in_b, t_cw_b), self.get_position(r_in_b, t_ccw_b), self.get_position(r_out_b, t_ccw_b), self.get_position(r_out_b, t_cw_over), self.get_position(r_out_b, t_cw_b)),
                    walls=face_walls)
            else:
                if c.exists_and_is_linked(c.inward):
                    if c.row - 1 in self.doubling_rows:
                        c_i = c.inward
                        row_length_i = len(self.rows_polar[c_i.row])
                        t_i = 2 * pi / row_length_i
                        t_over_i = pi / row_length_i
                        t_cw_over_i = (c_i.column * 2 + 1) * t_over_i
                        r_out_b_i = c_i.row + 0.5 + cs / 2
                        t_cw_b_i = (c_i.column + 0.5 - cs / 2) * t_i
                        t_ccw_b_i = (c_i.column + 0.5 + cs / 2) * t_i
                        if c_i.outward.index(c) == 0:
                            cv.add_face(
                                (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b_i, t_cw_b_i), self.get_position(r_out_b_i, t_cw_over_i)),
                                walls=(0, 3, 2, 1))
                        else:
                            cv.add_face(
                                (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b_i, t_cw_over_i), self.get_position(r_out_b_i, t_ccw_b_i)),
                                walls=(0, 3, 2, 1))
                    else:
                        r_inward_b = c.row - 0.5 + cs / 2
                        cv.add_face(
                            (self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_cw_b), self.get_position(r_inward_b, t_cw_b), self.get_position(r_inward_b, t_ccw_b)),
                            walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((0, 1))

                if c.exists_and_is_linked(c.ccw):
                    cv.add_face(
                        (self.get_position(r_out_b, t_ccw_b), self.get_position(r_in_b, t_ccw_b), self.get_position(r_in_b, t_ccw), self.get_position(r_out_b, t_ccw)),
                        walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((1, 2))

                if c.exists_and_is_linked(c.cw):
                    cv.add_face(
                        (self.get_position(r_in_b, t_cw_b), self.get_position(r_out_b, t_cw_b), self.get_position(r_out_b, t_cw), self.get_position(r_in_b, t_cw)),
                        walls=(0, 3, 2, 1))
                else:
                    face_walls.extend((3, 0))

                if c.row == self.rows - 1 or not c.is_linked_outward():
                    face_walls.extend((2, 3))

                cv.add_face(
                    (self.get_position(r_in_b, t_cw_b), self.get_position(r_in_b, t_ccw_b), self.get_position(r_out_b, t_ccw_b), self.get_position(r_out_b, t_cw_b)),
                    walls=face_walls)

        return cv

    def get_position(self, radius, angle):
        return Vector((radius * cos(angle), radius * sin(angle), 0))
