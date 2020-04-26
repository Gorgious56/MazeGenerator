import random
from typing import Iterable, Tuple, List, Generator
from mathutils import Vector
from math import pi, floor, cos, sin
from .cells import Cell, CellHex, CellOver, CellPolar, CellTriangle, CellUnder
from ..managers import space_rep_manager as sp_mgr
# from ..managers.mesh_manager import VG_DISPLACE
from . import constants as cst
from ..managers.distance_manager import Distances
from ..utils import event


class Grid:
    CELL_SIDES = 4
    CELL_TYPE = Cell

    def __init__(self, rows: int = 2, columns: int = 2, levels: int = 1, cell_size: int = 1, space_rep: int = 0, mask: Iterable[Tuple[int]] = None) -> None:
        self.rows: int = rows
        self.columns = columns
        self.levels = levels
        self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = []  # This container is used in some algorithms.
        self.space_rep = space_rep
        self.dead_ends_amount = 0
        self.distances = None
        self.longest_path = None

        self.mask = mask

        self.offset = self._get_offset()

        self.cell_size = cell_size

        self.number_of_sides = self.CELL_SIDES

        self.verts_indices = {}
        self.new_cell_evt = event.EventHandler(event.Event('New Cell'), self)

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

    def _get_offset(self) -> Vector:
        return Vector(((1 - self.columns) / 2, (1 - self.rows) / 2, 0))

    def prepare_grid(self) -> None:
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = self.CELL_TYPE(r, c, l) if self[c, r, l] is None else None
                    self.new_cell_evt(self[c, r, l])

    def next_row(self, cell: Cell, reverse: bool = False) -> Cell:
        """
        Returns the cell next row to the one passed as parameter
        Returns None if either cell exists

        Set reverse to True to get the cell in the previous row
        """
        if cell:
            return self[cell.column, cell.row + (-1 if reverse else 1), cell.level]

    def next_column(self, cell: Cell, reverse: bool = False) -> Cell:
        """
        Returns the cell next column to the one passed as parameter
        Returns None if either cell exists

        Set reverse to True to get the cell in the previous column
        """
        if cell:
            return self[cell.column + (-1 if reverse else 1), cell.row, cell.level]

    def next_level(self, cell: Cell, reverse: bool = False) -> Cell:
        """
        Returns the cell next level to the one passed as parameter
        Returns None if either cell exists

        Set reverse to True to get the cell in the previous level
        """
        return self[cell.column, cell.row, cell.level + (-1 if reverse else 1)]

    def init_cells_neighbors(self) -> None:
        if self.space_rep == int(sp_mgr.REP_BOX):
            rows = int(self.rows / 3)
            cols = int(self.columns / 2 - rows)
            for c in self.all_cells:
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
        else:
            for c in self.all_cells:
                c.set_neighbor(cst.NORTH, self.next_row(c))
                c.set_neighbor(cst.EAST, self.next_column(c))
                c.set_neighbor(cst.UP, self.next_level(c))

    def mask_ring(self, center_row: int, center_col: int, radius: float) -> None:
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

    def mask_patch(self, first_cell_x: int, first_cell_y: int, last_cell_x: int, last_cell_y: int) -> None:
        for c in range(first_cell_x, last_cell_x + 1):
            for r in range(first_cell_y, last_cell_y + 1):
                self[c, r] = 0

    def get_linked_cells(self) -> List[Cell]:
        return [c for c in self.all_cells if any(c.links)]

    def mask_cell(self, column: int, row: int) -> None:
        c = self[column, row]
        if c is not None:
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None
                c.unlink(n)

    def random_cell(self, _seed: int = None) -> Cell:
        if _seed:
            random.seed(_seed)
        try:
            return random.choice(self.all_cells)
        except IndexError:
            return None

    def get_random_linked_cell(self, _seed: int = None) -> Cell:
        if _seed:
            random.seed(_seed)
        try:
            return random.choice(self.get_linked_cells())
        except IndexError:
            return None

    def each_row(self) -> Generator[List[Cell], None, None]:
        """
        Travel the grid row by row, starting at index 0
        """
        cols = self.columns
        for l in range(self.levels):
            for r in range(self.rows):
                yield [c for c in self._cells[r * cols + l * self.size_2D: (r + 1) * cols + l * self.size_2D] if c]

    def each_level(self) -> Generator[List[Cell], None, None]:
        """
        Travel the grid level by level, starting at index 0
        """
        for l in range(self.levels):
            yield [c for c in self._cells[l * self.size_2D: (l + 1) * self.size_2D]]

    def each_cell(self) -> Generator[Cell, None, None]:
        for c in (c for c in self._cells if c):
            yield c

    @property
    def all_cells(self) -> List[Cell]:
        return [c for c in self._cells if c]

    @property
    def all_cells_with_a_link(self) -> List[Cell]:
        return [c for c in self._cells if c and c.has_any_link()]

    def get_dead_ends(self) -> List[Cell]:
        return [c for c in self.all_cells if len(c.links) == 1]

    def braid_dead_ends(self, braid: int = 0, _seed: int = None) -> int:
        """
        This will link each dead-end to a neighboring cell
        The method will favor other neighboring dead-ends to link to

        braid : Amount between 0 (no braid) and 100 (all dead-ends are braided)

        Returns the number of dead-ends after braiding
        """
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
        self.dead_ends_amount = dead_ends

    def sparse_dead_ends(self, sparse: int = 0, _seed: int = None) -> None:
        """
        This will sparse the maze by culling dead ends iteratively
        The cull is performed by unlinking the culled cell from all of its neighbors
        The maze will still be 'perfect' at the end of the method
        Depending of the maze algorithm, the method might stop before the expected sparsing value

        sparse : Amount between 0 (no cull) and 100 (all cells are culled)
        """
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
                except (StopIteration, AttributeError):
                    pass

    def shuffled_cells(self) -> List[Cell]:
        shuffled_cells = self.all_cells
        random.shuffle(shuffled_cells)
        return shuffled_cells

    def get_cell_center(self, cell: Cell) -> Vector:
        # return Vector((cell.column + cell.level * (self.columns + 1), cell.row, 0)) + self.offset
        return Vector((cell.column + cell.level * (self.columns + 1), cell.row, 0))

    def get_cell_positions(self, cell):
        """
        3 2
        0 1
        """
        size = self.cell_size
        center = self.get_cell_center(cell)
        return center + Vector(((-size / 2), (-size / 2), 0)), center + Vector(((size / 2), (-size / 2), 0)), center + Vector(((size / 2), (size / 2), 0)), center + Vector(((-size / 2), (size / 2), 0))

    def calc_distances(self, props):
        distances = Distances(self.get_random_linked_cell(_seed=props.seed))
        distances.get_distances()
        new_start, distance = distances.max
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max

        longest_path = distances.path_to(goal).path

        # Avoid flickering when the algorithm randomly chooses start and end cells.
        start = longest_path[0]
        start = (start.row, start.column, start.level)
        last_start = props.maze_last_start_cell
        last_start = (last_start[0], last_start[1], last_start[2])
        if start != last_start:
            goal = longest_path[-1]
            goal = (goal.row, goal.column, goal.level)
            if goal == last_start:
                distances.reverse()
            else:
                props.maze_last_start_cell = start
        # End.
        self.distances = distances
        self.longest_path = longest_path


class GridHex(Grid):
    CELL_SIDES = 6
    CELL_TYPE = CellHex

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 3 - self.columns / 2, 1 - self.rows * (3 ** 0.5) / 2, 0))

    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            row, col = c.row, c.column
            north_diagonal = row + (1 if col % 2 == 0 else 0)

            # Neighbor 0 : NE
            c.set_neighbor(0, self[col + 1, north_diagonal])
            # Neighbor 1 : N
            c.set_neighbor(1, self[col, row + 1])
            # Neighbor 2 : NW
            c.set_neighbor(2, self[col - 1, north_diagonal])
            # # Neighbor 3 : SW

    def get_relative_positions(self, size: float) -> Tuple[Vector]:
        """
        Returns the positions of each corner of the cell
        """
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

    def init_cells_neighbors(self) -> None:
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

    def each_row(self) -> Generator[List[Cell], None, None]:
        """
        Travel the grid row by row, starting at index 0
        """
        for r in self.rows_polar:
            yield r

    def each_cell(self) -> Generator[Cell, None, None]:
        for r in self.each_row():
            for c in r:
                if c:
                    yield c

    @property
    def all_cells(self):
        cells = []
        # return [c for c in row for row in self.each_row() if c]
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
        # The faces are all inverted but reverting all of the calculations is a big hassle.
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

    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            if c.is_upright():
                c.set_neighbor(0, self.next_column(c))
                c.set_neighbor(1, self.next_column(c, reverse=True))
                c.set_neighbor(2, self.next_row(c, reverse=True))

    def get_cell_center(self, c):
        return Vector((c.column * 0.5, c.row * (3 ** 0.5) / 2, 0))

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 4, -self.rows / 3, 0))

    def get_cell_positions(self, cell):
        """
         2      IF UPRIGHT ELSE   2 1
        0 1                        0
        """
        size = self.cell_size
        center = self.get_cell_center(cell)

        half_width = size / 2

        height = size * (3 ** 0.5) / 2
        half_height = height / 2

        if cell.is_upright():
            base_y = - half_height
            apex_y = half_height
        else:
            base_y = half_height
            apex_y = - half_height

        north_or_south = Vector((0, apex_y, 0)) + center
        west = Vector((-half_width, base_y, 0)) + center
        east = Vector((half_width, base_y, 0)) + center
        return (west, east, north_or_south) if cell.is_upright() else (north_or_south, east, west)


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal: bool = False, weave: int = 0, **kwargs):
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
