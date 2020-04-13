import random
from mathutils import Vector
from math import pi, floor, cos, sin
from .cells import Cell, CellHex, CellOver, CellPolar, CellTriangle, CellUnder
from ...visual import space_rep_manager as sp_mgr
from ...visual.cell_visual import DISPLACE
from . import constants as cst


class Grid:
    CELL_SIDES = 4
    CELL_TYPE = Cell

    def __init__(self, rows=2, columns=2, levels=1, cell_size=1, space_rep=0, mask=None):
        self.rows = rows
        self.columns = columns
        self.levels = levels
        self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = []  # This container is used in some algorithms.
        self.space_rep = space_rep

        self.mask = mask

        self.offset = self.get_offset()

        self.cell_size = cell_size

        self.number_of_sides = self.CELL_SIDES

        self.relative_positions_inset = self.get_relative_positions(self.cell_size)
        self.relative_positions_one = self.get_relative_positions(1)
        self.relative_positions_out = self.get_relative_positions_out()

        self.prepare_grid()
        self.configure_cells()

    def get_offset(self):
        return Vector(((1 - self.columns) / 2, (1 - self.rows) / 2, 0))

    def __delitem__(self, key):
        del self._cells[key[0] + key[1] * self.columns]

    def __getitem__(self, key):
        key = list(key)
        if len(key) == 2:
            key.append(0)
        if self.space_rep in (int(sp_mgr.REP_CYLINDER), int(sp_mgr.REP_MEOBIUS), int(sp_mgr.REP_TORUS), int):
            if key[0] == -1:
                key[0] = self.columns - 1
            elif key[0] == self.columns:
                key[0] = 0
            if self.space_rep == int(sp_mgr.REP_TORUS):
                if key[1] == -1:
                    key[1] = self.rows - 1
                elif key[1] == self.rows:
                    key[1] = 0
        return self._cells[key[0] + key[1] * self.columns + key[2] * self.size_2D] \
            if (self.columns > key[0] >= 0 and self.rows > key[1] >= 0 and self.levels > key[2] >= 0) else None

    def __setitem__(self, key, value):
        if len(key) == 2:
            self.__setitem__((key[0], key[1], 0), value)
        else:
            self._cells[key[0] + key[1] * self.columns + key[2] * self.size_2D] = value

    def prepare_grid(self):
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = self.CELL_TYPE(r, c, l) if self[c, r, l] is None else None

    def next_row(self, cell, reverse=False):
        return self[cell.column, cell.row + (-1 if reverse else 1), cell.level]

    def next_column(self, cell, reverse=False):
        return self[cell.column + (-1 if reverse else 1), cell.row, cell.level]

    def next_level(self, cell, reverse=False):
        return self[cell.column, cell.row, cell.level + (-1 if reverse else 1)]

    def configure_cells(self):
        if self.space_rep != int(sp_mgr.REP_BOX):
            for c in self.all_cells():
                c.set_neighbor(cst.NORTH, self.next_row(c))
                c.set_neighbor(cst.EAST, self.next_column(c))
                c.set_neighbor(cst.UP, self.next_level(c))
        else:
            rows = int(self.rows / 3)
            cols = int(self.columns / 2 - rows)
            for c in self.all_cells():
                row, col, level = c.row, c.column, c.level
                # North :
                if row == 2 * rows - 1:
                    if col < rows:
                        c.set_neighbor(cst.NORTH, self[rows, 3 * rows - col - 1, level])
                        c.neighbor(cst.NORTH).set_neighbor(cst.WEST, c)
                    elif rows + cols <= col < 2 * rows + cols:
                        c.set_neighbor(cst.NORTH, self[rows + cols - 1, rows - cols + col, level])
                        c.neighbor(cst.NORTH).set_neighbor(cst.EAST, c)
                    elif col >= 2 * rows + cols:
                        c.set_neighbor(cst.NORTH, self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level])
                        c.neighbor(cst.NORTH).set_neighbor(cst.NORTH, c)
                    else:
                        c.set_neighbor(cst.NORTH, self[col, row + 1, level])
                        c.neighbor(cst.NORTH).set_neighbor(cst.SOUTH, c)
                elif not c.neighbor(cst.NORTH):
                    c.set_neighbor(cst.NORTH, self[col, row + 1, level])
                    if c.neighbor(cst.NORTH):
                        c.neighbor(cst.NORTH).set_neighbor(cst.SOUTH, c)
                # West :
                if not c.neighbor(cst.WEST):
                    c.set_neighbor(cst.WEST, self[col - 1, row, level])
                    if c.neighbor(cst.WEST):
                        c.neighbor(cst.WEST).set_neighbor(cst.EAST, c)
                # South :
                if row == rows:
                    if col < rows:
                        c.set_neighbor(cst.SOUTH, self[rows, col, level])
                        c.neighbor(cst.SOUTH).set_neighbor(cst.WEST, c)
                    elif rows + cols <= col < 2 * rows + cols:
                        c.set_neighbor(cst.SOUTH, self[rows + cols - 1, 2 * rows + cols - 1 - col, level])
                        c.neighbor(cst.SOUTH).set_neighbor(cst.EAST, c)
                    elif col >= 2 * rows + cols:
                        c.set_neighbor(cst.SOUTH, self[3 * rows + 2 * cols - 1 - col, 0, level])
                        c.neighbor(cst.SOUTH).set_neighbor(cst.SOUTH, c)
                    else:
                        c.set_neighbor(cst.SOUTH, self[col, row - 1, level])
                        c.neighbor(cst.SOUTH).set_neighbor(cst.NORTH, c)

    def mask_patch(self, first_cell_x, first_cell_y, last_cell_x, last_cell_y):
        for c in range(first_cell_x, last_cell_x + 1):
            for r in range(first_cell_y, last_cell_y + 1):
                self[c, r] = 0

    def get_linked_cells(self):
        return [c for c in self.all_cells() if any(c.links)]

    def mask_cell(self, column, row):
        c = self[column, row]
        if c is not None:
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None
                c.unlink(n)

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            random.seed(_seed)
        try:
            return random.choice(self.all_cells()) if filter_mask else random.choice(self.all_cells())
        except IndexError:
            return None

    def get_random_linked_cell(self, _seed=None):
        if _seed:
            random.seed(_seed)
        try:
            return random.choice(self.get_linked_cells())
        except IndexError:
            return None

    def each_row(self):
        cols = self.columns
        for l in range(self.levels):
            for r in range(self.rows):
                yield [c for c in self._cells[r * cols + l * self.size_2D: (r + 1) * cols + l * self.size_2D] if c]

    def each_level(self):
        for l in range(self.levels):
            yield [c for c in self._cells[l * self.size_2D: (l + 1) * self.size_2D]]

    def each_cell(self):
        for c in self.all_cells():
            yield c

    def all_cells(self):
        return [c for c in self._cells if c]

    def get_dead_ends(self):
        return [c for c in self.all_cells() if len(c.links) == 1]

    def braid_dead_ends(self, braid=0, _seed=None):
        dead_ends_shuffle = self.get_dead_ends()
        dead_ends = len(dead_ends_shuffle)
        if braid > 0:
            braid /= 100
            random.seed(_seed)

            random.shuffle(dead_ends_shuffle)
            stop_index = int(len(dead_ends_shuffle) * min(max(0, braid), 1))
            for c in dead_ends_shuffle[0:stop_index]:
                if len(c.links) == 1:
                    unconnected_neighbors = [n for n in c.neighbors if n not in c.links and n.has_any_link()]
                    if len(unconnected_neighbors) > 0:
                        best = [n for n in unconnected_neighbors if len(n.links) < 2]
                        if best:
                            dead_ends -= 1
                        else:
                            best = unconnected_neighbors
                        c.link(random.choice(best))
                        dead_ends -= 1
        return dead_ends

    def sparse_dead_ends(self, sparse=0, braid=0, _seed=None):
        max_cells_to_cull = len(self.get_linked_cells()) * (sparse / 100) - 2
        culled_cells = 0
        while culled_cells < max_cells_to_cull:
            dead_ends = self.get_dead_ends()
            if not any(dead_ends):
                return
            for c in dead_ends:
                try:
                    c.unlink(next(iter(c.links)))
                    culled_cells += 1
                    if culled_cells >= max_cells_to_cull:
                        return
                except StopIteration:
                    pass
                except AttributeError:
                    pass

    def shuffled_cells(self):
        shuffled_cells = self.all_cells()
        random.shuffle(shuffled_cells)
        return shuffled_cells

    def mask_ring(self, center_row, center_col, radius):
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

    def get_blueprint(self):
        return [self.set_cell_visuals(c) for c in self.get_linked_cells()]

    def get_cell_center(self, c):
        return Vector((c.column + c.level * (self.columns + 1), c.row, 0)) + self.offset

    def get_relative_positions_out(self):
        cs = self.cell_size
        pos_one, pos_out = self.relative_positions_one, []
        for i in range(self.number_of_sides):
            pos_out.append((pos_one[i] * (1 + cs) + pos_one[(i + 1) % self.number_of_sides] * (1 - cs)) / 2)
            pos_out.append((pos_one[i] * (1 - cs) + pos_one[(i + 1) % self.number_of_sides] * (1 + cs)) / 2)
        return pos_out

    def get_relative_positions(self, size):
        top_right = Vector(((size / 2), (size / 2), 0))
        top_left = Vector(((-size / 2), (size / 2), 0))
        bot_left = Vector(((-size / 2), (-size / 2), 0))
        bot_right = Vector(((size / 2), (-size / 2), 0))
        return top_right, top_left, bot_left, bot_right

    def get_cell_pos_offset(self, cell, center):
        if self.cell_size == 1:
            return [center + vec for vec in self.relative_positions_one], (), ()
        else:
            return [center + vec for vec in self.relative_positions_one], \
                [center + vec for vec in self.relative_positions_inset], \
                [center + vec for vec in self.relative_positions_out]

    def set_cell_visuals(self, c):
        cv = c.visual
        center = self.get_cell_center(c)
        walls_face = []
        pos_one, pos_in, pos_out = self.get_cell_pos_offset(c, center)
        for i in range(self.number_of_sides):
            if c.get_wall_mask()[i]:
                walls_face.extend((i, (i + 1) % self.number_of_sides))
            elif self.cell_size != 1:
                cv.add_face((pos_in[i], pos_out[2 * i], pos_out[(i * 2) + 1], pos_in[(i + 1) % self.number_of_sides]), walls=(0, 1, 2, 3), vertices_levels=(1, 0, 0, 1))

        cv.add_face(
            ([(pos_one if self.cell_size == 1 else pos_in)[i % self.number_of_sides] for i in range(self.number_of_sides)]),
            walls=walls_face,
            vertices_levels=[1] * self.number_of_sides)

        if self.levels > 0:
            dz = 0.1
            dd = self.cell_size / 4
            if c.neighbor_index_exists_and_is_linked(cst.UP):
                cv.add_face((center + Vector((dd * 3 / 2, 0, dz)), center + Vector((dd / 2, dd, dz)), center + Vector((dd / 2, -dd, dz))))
            if c.neighbor_index_exists_and_is_linked(cst.DOWN):
                cv.add_face((center + Vector((- dd * 3 / 2, 0, dz)), center + Vector((- dd / 2, -dd, dz)), center + Vector((- dd / 2, dd, dz))))
        return cv


class GridHex(Grid):
    CELL_SIDES = 6
    CELL_TYPE = CellHex

    def get_offset(self):
        return Vector((-self.columns / 3 - self.columns / 2, 1 - self.rows * (3 ** 0.5) / 2, 0))

    # def prepare_grid(self):
    #     for r in range(self.rows):
    #         for c in range(self.columns):
    #             self[c, r] = CellHex(r, c)

    def configure_cells(self):
        for c in self.each_cell():
            row, col = c.row, c.column

            if col % 2 == 0:
                north_diagonal = row + 1
                south_diagonal = row
            else:
                north_diagonal = row
                south_diagonal = row - 1

            # Neighbor 0 : NE
            c.set_neighbor(0, self[col + 1, north_diagonal])
            # Neighbor 1 : N
            c.set_neighbor(1, self[col, row + 1])
            # Neighbor 2 : NW
            c.set_neighbor(2, self[col - 1, north_diagonal])
            # # Neighbor 3 : SW
            # c.set_neighbor(3, self[col - 1, south_diagonal])
            # # Neighbor 4 : S
            # c.set_neighbor(4, self[col, row - 1])
            # # Neighbor 5 : SE
            # c.set_neighbor(5, self[col + 1, south_diagonal])

    def get_relative_positions(self, size):
        a_size = size / 2
        b_size = size * (3 ** 0.5) / 2

        east = Vector((size, 0, 0))
        north_east = Vector((a_size, b_size, 0))
        north_west = Vector((-a_size, b_size, 0))
        west = Vector((- size, 0, 0))
        south_west = Vector((-a_size, -b_size, 0))
        south_east = Vector((a_size, -b_size, 0))
        return east, north_east, north_west, west, south_west, south_east

    def get_cell_center(self, c):
        return Vector([1 + 3 * c.column / 2, - (3 ** 0.5) * ((1 + c.column % 2) / 2 - c.row), 0]) + self.offset


class GridPolar(Grid):
    CELL_TYPE = CellPolar

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

    def next_column(self, cell, reverse=False):
        return self.rows_polar[cell.row][cell.column + 1] if 0 <= cell.column < self.row_length(cell.row) - 1 else None

    def next_row(self, cell, reverse=False):
        return random.choice(cell.outward) if cell.outward else None

    def next_level(self, cell, reverse=False):
        return None

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
                row_length = self.row_length(c.row)
                c.ccw = self[row, (col + 1) % row_length]
                c.cw = self[row, col - 1]

                ratio = row_length / self.row_length(c.row - 1)
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
            random.seed(_seed)
        return random.choice([c for c in random.choice(self.rows_polar)])

    def set_cell_visuals(self, c):
        # The faces are all reversed but inverting all of the calculations is a big hassle.
        # Hacky but works.
        cv = c.visual
        row_length = self.row_length(c.row)
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

    def row_length(self, row):
        return len(self.rows_polar[row])


class GridTriangle(Grid):
    CELL_SIDES = 3
    CELL_TYPE = CellTriangle

    def __init__(self, rows, columns, levels, cell_size, space_rep, mask=None):
        super().__init__(rows, columns, levels, cell_size, space_rep, mask)
        self.relative_positions_inset_down = self.get_relative_positions(self.cell_size, upright=False)
        self.relative_positions_one_down = self.get_relative_positions(1, upright=False)
        self.relative_positions_out_down = self.get_relative_positions_out_down()

    def configure_cells(self):
        for c in self.each_cell():
            if c.is_upright():
                c.set_neighbor(0, self.next_column(c))
                c.set_neighbor(1, self.next_column(c, reverse=True))
                c.set_neighbor(2, self.next_row(c, reverse=True))

    def get_relative_positions_out_down(self):
        cs = self.cell_size
        pos_one, pos_out = self.relative_positions_one_down, []
        for i in range(self.number_of_sides):
            pos_out.append((pos_one[i] * (1 + cs) + pos_one[(i + 1) % self.number_of_sides] * (1 - cs)) / 2)
            pos_out.append((pos_one[i] * (1 - cs) + pos_one[(i + 1) % self.number_of_sides] * (1 + cs)) / 2)
        return pos_out

    def get_cell_center(self, c):
        return Vector((c.column * 0.5, c.row * (3 ** 0.5) / 2, 0)) + self.offset

    def get_offset(self):
        return Vector((-self.columns / 4, -self.rows / 3, 0))

    def get_relative_positions(self, size, upright=True):
        half_width = size / 2

        height = size * (3 ** 0.5) / 2
        half_height = height / 2

        if upright:
            base_y = - half_height
            apex_y = half_height
        else:
            base_y = half_height
            apex_y = - half_height

        north_or_south = Vector((0, apex_y, 0))
        west = Vector((-half_width, base_y, 0))
        east = Vector((half_width, base_y, 0))
        return (east, north_or_south, west) if upright else (west, north_or_south, east)

    def get_cell_pos_offset(self, cell, center):
        if cell.is_upright():
            return super().get_cell_pos_offset(cell, center)
        else:
            if self.cell_size == 1:
                return [center + vec for vec in self.relative_positions_one_down], (), ()
            else:
                return [center + vec for vec in self.relative_positions_one_down], \
                    [center + vec for vec in self.relative_positions_inset_down], \
                    [center + vec for vec in self.relative_positions_out_down]


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal=False, weave=0, **kwargs):
        self.use_kruskal = use_kruskal
        self.weave = weave / 100
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        if self.use_kruskal:
            CellOver.get_neighbors = lambda: Cell.neighbors
        else:
            CellOver.get_neighbors = lambda: CellOver.neighbors_copy

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = CellOver(r, c, l) if self[c, r, l] is None else None
                    self[c, r, l].request_tunnel_under += lambda cell, neighbor: self.tunnel_under(neighbor)

    def tunnel_under(self, cell_over):
        """
        Tunnel under the specified cell of type 'CellOver'

        Returns the resulting 'CellUnder'
        """
        self._cells.append(CellUnder(cell_over))
        return self._cells[-1]

    def set_cell_visuals(self, c):
        cv = super().set_cell_visuals(c)
        if type(c) is CellUnder:
            for f in cv.faces:
                f.set_vertex_group(DISPLACE, [v_level for v_level in f.vertices_levels])
                f.walls = None
        elif c.has_cell_under:
            for f in cv.faces:
                f.walls = None

        return cv
