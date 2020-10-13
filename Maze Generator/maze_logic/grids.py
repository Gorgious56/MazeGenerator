"""
Handles data access and modifications relative to a maze's grid
"""

import random
from typing import Iterable, Tuple, List, Generator
from math import pi, floor, cos, sin
from mathutils import Vector
from .cells import Cell, CellOver, CellUnder
from . import constants as cst
from .distance import Distances
from ..managers import space_rep_manager as sp_mgr
from ..utils import event, union_find


class Grid:
    """
    Handles data access and modifications relative to a maze's grid
    """
    def __init__(self, rows: int = 2, columns: int = 2, levels: int = 1, cell_size: float = 1.0, space_rep: int = 0, mask: Iterable[Tuple[int]] = None, init_cells=True) -> None:
        self.rows: int = rows
        self.columns = columns
        self.levels = levels
        if init_cells:
            self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = 0  # This container is used in some algorithms.
        self.space_rep = space_rep

        self.dead_ends = []
        self.max_links_per_cell = 0
        self.groups = set()
        self.distances = None
        self.longest_path = None

        self.mask = mask

        self.offset = self._get_offset()

        self.cell_size = cell_size

        # self.verts_indices = {}
        self.new_cell_evt = event.EventHandler(event.Event('New Cell'), self)

        self._union_find = None
        self.verts = []

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

    @property
    def dead_ends_amount(self):
        return len(self.dead_ends)

    def __setitem__(self, key, value):
        if len(key) == 2:
            self.__setitem__((key[0], key[1], 0), value)
        else:
            self._cells[key[0] + key[1] * self.columns + key[2] * self.size_2D] = value

    def _get_offset(self) -> Vector:
        return Vector(((1 - self.columns) / 2, (1 - self.rows) / 2, 0))

    def mask_cells(self) -> None:
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

    def create_cell(self, row, column, level) -> Cell:
        size = self.cell_size
        if self[column, row, level] is None:
            new_cell = Cell(
                row, column, level,
                # neighbors_return=(cst.SOUTH, cst.EAST, cst.NORTH, cst.WEST),
                half_neighbors=(0, 1),
            )
            center = Vector((column + level * (self.columns + 1), row, 0))

            new_cell.first_vert_index = len(self.verts)
            self.verts.extend((
                center + Vector((size / 2, size / 2, 0)),
                center + Vector((-size / 2, size / 2, 0)),
                center + Vector((-size / 2, -size / 2, 0)),
                center + Vector((size / 2, -size / 2, 0))))
            return new_cell

    def prepare_grid(self) -> None:
        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    new_cell = self.create_cell(r, c, l)
                    self[c, r, l] = new_cell
                    self.new_cell_evt(new_cell)

    def prepare_union_find(self) -> None:
        self._union_find = union_find.UnionFind(self.all_cells)

    def connected(self, cell_a, cell_b) -> bool:
        return self._union_find.connected(cell_a, cell_b)

    def find(self, cell):
        return self._union_find.find(cell)

    def delta_cell(self, cell: Cell, column: int = 0, row: int = 0, level: int = 0) -> Cell:
        return self[cell.column + column, cell.row + row, cell.level + level]

    def get_columns_this_row(self, row):
        return self.columns

    def init_cells_neighbors(self) -> None:
        if self.space_rep == int(sp_mgr.REP_BOX):
            rows = int(self.rows / 3)
            cols = int(self.columns / 2 - rows)
            for c in self.all_cells:
                row, col, level = c.row, c.column, c.level
                # North :
                if row == 2 * rows - 1:
                    if col < rows:
                        c.set_neighbor(cst.NORTH, self[rows, 3 * rows - col - 1, level], cst.SOUTH)
                        c.neighbor(cst.NORTH).set_neighbor(cst.WEST, c, cst.EAST)
                    elif rows + cols <= col < 2 * rows + cols:
                        c.set_neighbor(cst.NORTH, self[rows + cols - 1, rows - cols + col, level], cst.SOUTH)
                        c.neighbor(cst.NORTH).set_neighbor(cst.EAST, c, cst.SOUTH)
                    elif col >= 2 * rows + cols:
                        c.set_neighbor(cst.NORTH, self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level], cst.SOUTH)
                        c.neighbor(cst.NORTH).set_neighbor(cst.NORTH, c, cst.SOUTH)
                    else:
                        c.set_neighbor(cst.NORTH, self[col, row + 1, level], cst.SOUTH)
                        c.neighbor(cst.NORTH).set_neighbor(cst.SOUTH, c, cst.NORTH)
                elif not c.neighbor(cst.NORTH):
                    c.set_neighbor(cst.NORTH, self[col, row + 1, level], cst.SOUTH)
                    if c.neighbor(cst.NORTH):
                        c.neighbor(cst.NORTH).set_neighbor(cst.SOUTH, c, cst.NORTH)
                # West :
                if not c.neighbor(cst.WEST):
                    c.set_neighbor(cst.WEST, self[col - 1, row, level], cst.EAST)
                    if c.neighbor(cst.WEST):
                        c.neighbor(cst.WEST).set_neighbor(cst.EAST, c, cst.WEST)
                # South :
                if row == rows:
                    if col < rows:
                        c.set_neighbor(cst.SOUTH, self[rows, col, level], cst.NORTH)
                        c.neighbor(cst.SOUTH).set_neighbor(cst.WEST, c, cst.EAST)
                    elif rows + cols <= col < 2 * rows + cols:
                        c.set_neighbor(cst.SOUTH, self[rows + cols - 1, 2 * rows + cols - 1 - col, level], cst.NORTH)
                        c.neighbor(cst.SOUTH).set_neighbor(cst.EAST, c, cst.WEST)
                    elif col >= 2 * rows + cols:
                        c.set_neighbor(cst.SOUTH, self[3 * rows + 2 * cols - 1 - col, 0, level], cst.NORTH)
                        c.neighbor(cst.SOUTH).set_neighbor(cst.SOUTH, c, cst.NORTH)
                    else:
                        c.set_neighbor(cst.SOUTH, self[col, row - 1, level], cst.NORTH)
                        c.neighbor(cst.SOUTH).set_neighbor(cst.NORTH, c, cst.SOUTH)
        else:
            for c in self.all_cells:
                c.set_neighbor(cst.NORTH, self.delta_cell(c, row=1), cst.SOUTH)
                c.set_neighbor(cst.EAST, self.delta_cell(c, column=1), cst.WEST)
                c.set_neighbor(cst.UP, self.delta_cell(c, level=1), cst.DOWN)

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
            self.masked_cells += 1
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.get_neighbor_return(i)] = None
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

    def calc_state(self):
        self.dead_ends = []
        self.max_links_per_cell = 0
        self.groups = set()
        for c in self.all_cells:
            links = len(c.links)
            if links == 1:
                self.dead_ends.append(c)
            self.max_links_per_cell = max(links, self.max_links_per_cell)
            self.groups.add(c.group)

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
            self.dead_ends = [c for c in self.all_cells if c and len(c.links) == 1]
            if not any(self.dead_ends):
                return
            random.shuffle(self.dead_ends)
            for c in self.dead_ends:
                try:
                    c.unlink(next(iter(c.links)))
                    # self.dead_ends.remove(c)
                    culled_cells += 1
                    if culled_cells >= max_cells_to_cull:
                        return
                except (StopIteration, AttributeError):
                    # self.dead_ends.remove(c)
                    pass

    def braid_dead_ends(self, braid: int = 0, _seed: int = None) -> int:
        """
        This will link each dead-end to a neighboring cell
        The method will favor other neighboring dead-ends to link to

        braid : Amount between 0 (no braid) and 100 (all dead-ends are braided)

        Returns the number of dead-ends after braiding
        """
        if braid > 0:
            self.dead_ends = [c for c in self.all_cells if c and len(c.links) == 1]
            braid /= 100
            random.seed(_seed)
            dead_ends_to_keep = int(len(self.dead_ends) * min(max(0, 1 - braid), 1))
            random.shuffle(self.dead_ends)
            while self.dead_ends and len(self.dead_ends) >= dead_ends_to_keep:
                c = self.dead_ends[0]
                neighbors_sorted_by_links = sorted([n for n in c.neighbors if n not in c.links and n.has_any_link()], key=lambda c: len(c.links))
                if neighbors_sorted_by_links:
                    best_neighbor = neighbors_sorted_by_links[0]
                    self.link(c, best_neighbor)
                    self.max_links_per_cell = max(len(c.links), len(best_neighbor.links), self.max_links_per_cell)
                    self.dead_ends.remove(c)
                    if best_neighbor in self.dead_ends:
                        self.dead_ends.remove(best_neighbor)
                else:
                    self.dead_ends.remove(c)

    def shuffled_cells(self) -> List[Cell]:
        shuffled_cells = self.all_cells
        random.shuffle(shuffled_cells)
        return shuffled_cells

    def calc_distances(self, props):
        distances = Distances(self.get_random_linked_cell(_seed=props.seed))
        distances.get_distances()
        new_start, distance = distances.max
        distances = Distances(new_start)
        distances.get_distances()
        goal, max_distance = distances.max

        longest_path = distances.path_to(goal).path
        if longest_path and longest_path[0] is not None:
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

    def link(self, cell_a, cell_b, bidirectional=True):
        linked_cells = cell_a.link(cell_b, bidirectional)
        if linked_cells and all(linked_cells):
            self._union_find.union(linked_cells[0], linked_cells[1])
        return linked_cells

    def unlink(self, cell_a, cell_b):
        cell_a.unlink(cell_b)


class GridHex(Grid):
    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            row, col = c.row, c.column
            north_diagonal = row + (1 if col % 2 == 0 else 0)
            # Neighbor 0 : NE
            c.set_neighbor(0, self[col + 1, north_diagonal], 3)
            # Neighbor 1 : N
            c.set_neighbor(1, self[col, row + 1], 4)
            # Neighbor 2 : NW
            c.set_neighbor(2, self[col - 1, north_diagonal], 5)

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 3 - self.columns / 2, 1 - self.rows * (3 ** 0.5) / 2, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            new_cell = Cell(
                row, column, level,
                corners=6,
                half_neighbors=(0, 1, 2))

            center = Vector((1 + 3 * column / 2, - (3 ** 0.5) * ((1 + column % 2) / 2 - row), 0))
            size = self.cell_size
            new_cell.first_vert_index = len(self.verts)
            a_size = size / 2
            b_size = size * (3 ** 0.5) / 2

            east = Vector((size, 0, 0)) + center
            north_east = Vector((a_size, b_size, 0)) + center
            north_west = Vector((-a_size, b_size, 0)) + center
            west = Vector((- size, 0, 0)) + center
            south_west = Vector((-a_size, -b_size, 0)) + center
            south_east = Vector((a_size, -b_size, 0)) + center
            self.verts.extend((east, north_east, north_west, west, south_west, south_east))
            return new_cell


class GridPolar(Grid):
    def __init__(self, rows, columns, levels, cell_size=1, space_rep=0, branch_polar=1, *args, **kwargs):
        # self.rows_polar = []
        cell_size = max(0, cell_size)
        super().__init__(rows=rows, columns=0, levels=levels, space_rep='1', cell_size=cell_size, init_cells=False, *args, **kwargs)

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

            columns = previous_columns * round(circumference * self.branch / previous_columns / row_height)  # Prev count * ratio. Place multiplier here
            if columns != previous_columns:
                self.doubling_rows.append(r - 1)
            self._cells.extend([None] * columns)

    def __delitem__(self, key):
        del self[key[0], key[1]]

    def __getitem__(self, key):
        key = list(key)
        if 0 <= key[1] < self.rows:
            if key[1] == self.rows - 1:
                row = self._cells[self.row_begin_index[key[1]]::]
            else:
                row = self._cells[self.row_begin_index[key[1]]:self.row_begin_index[key[1] + 1]]
            if key[0] == len(row):
                key[0] = 0
            elif key[0] == -1:
                key[0] = len(row) - 1
            return row[key[0]]

    def __setitem__(self, key, value):
        key = list(key)
        if 0 <= key[1] < self.rows:
            if key[1] == self.rows - 1:
                row = self._cells[self.row_begin_index[key[1]]::]
            else:
                row = self._cells[self.row_begin_index[key[1]]:self.row_begin_index[key[1] + 1]]
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
        return self.row_begin_index[row + 1] - self.row_begin_index[row] if row < self.rows - 1 else len(self._cells) - self.row_begin_index[row]

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
                yield self._cells[self.row_begin_index[i]:self.row_begin_index[i + 1]]
            else:
                yield self._cells[self.row_begin_index[i]::]

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
            return (r_out_ccw, r_in_ccw, r_in_cw, r_out_cw, self.get_position(r_out, (2 * cell.column + 1) * 2 * pi / self.get_columns_this_row(cell.row + 1)))
        else:
            return (r_out_ccw, r_in_ccw, r_in_cw, r_out_cw)

    def _get_offset(self) -> Vector:
        return Vector((0, 0, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            if row == 0:
                new_cell = Cell(
                    row, column, level,
                    corners=0,
                    half_neighbors=[])
            else:
                new_cell = Cell(
                    row, column, level,
                    corners=4,
                    half_neighbors=(0, 1))
            return new_cell


class GridTriangle(Grid):
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
            new_cell = Cell(
                row, column, level,
                corners=3,
                half_neighbors=(0, 1, 2) if up_right else [])

            center = Vector((column * 0.5, row * cst.SQRT3_OVER2, 0))
            size = self.cell_size
            new_cell.first_vert_index = len(self.verts)

            half_width = size / 2
            height = size * (3 ** 0.5) / 2
            half_height = height / 2

            if up_right:
                base_y = - half_height
                apex_y = half_height
                self.verts.extend((Vector((half_width, base_y, 0)) + center, Vector((0, apex_y, 0)) + center, Vector((-half_width, base_y, 0)) + center))
            else:
                base_y = half_height
                apex_y = - half_height
                self.verts.extend((Vector((-half_width, base_y, 0)) + center, Vector((0, apex_y, 0)) + center, Vector((half_width, base_y, 0)) + center))

            return new_cell


class GridOctogon(Grid):
    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            size = self.cell_size * 2
            if (row + column) % 2 == 0:
                new_cell = Cell(
                    row, column, level,
                    corners=8,
                    half_neighbors=(0, 1, 2, 3))
                center = Vector((column + level * (self.columns + 1), row, 0)) * 2
                new_cell.first_vert_index = len(self.verts)

                s_q = size * 0.25
                s_tq = size * 0.75
                self.verts.extend((
                    Vector((s_q, s_tq, 0)) + center,
                    Vector((-s_q, s_tq, 0)) + center,
                    Vector((-s_tq, s_q, 0)) + center,
                    Vector((-s_tq, -s_q, 0)) + center,
                    Vector((-s_q, -s_tq, 0)) + center,
                    Vector((s_q, -s_tq, 0)) + center,
                    Vector((s_tq, -s_q, 0)) + center,
                    Vector((s_tq, s_q, 0)) + center))
            else:
                new_cell = Cell(
                    row, column, level,
                    corners=4,
                    half_neighbors=(0, 1))
                center = Vector((column + level * (self.columns + 1), row , 0)) * 2

                new_cell.first_vert_index = len(self.verts)
                self.verts.extend((
                    center + Vector(((size / 4), (size / 4), 0)),
                    center + Vector(((-size / 4), (size / 4), 0)),
                    center + Vector(((-size / 4), (-size / 4), 0)),
                    center + Vector(((size / 4), (-size / 4), 0))))
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


class GridDodecagon(Grid):
    def _get_offset(self) -> Vector:
        return Vector((-0.5 - self.columns, - (self.rows // 3) * 7 / 8, 0))

    def create_cell(self, row, column, level) -> Cell:
        if self[column, row, level] is None:
            size = self.cell_size * 2
            if row % 3 == 0:  # Up triangle
                new_cell = Cell(
                    row, column, level,
                    corners=3,
                    half_neighbors=(1,))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 7 / 4 * (row / 3) + 1 / 4, 0))
                new_cell.first_vert_index = len(self.verts)
                self.verts.extend((Vector((size / 8, 0, 0)) + center, Vector((0, size / 4, 0)) + center, Vector((-size / 8, 0, 0)) + center))
            elif (row - 2) % 3 == 0:  # Down trianlge
                new_cell = Cell(
                    row, column, level,
                    corners=3,
                    half_neighbors=(0, 2))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 7 / 4 * (((row - 2) / 3) + 1), 0))
                new_cell.first_vert_index = len(self.verts)
                self.verts.extend((Vector((-size / 8, 0, 0)) + center, Vector((0, -size / 4, 0)) + center, Vector((size / 8, 0, 0)) + center))
            else:
                new_cell = Cell(
                    row, column, level,
                    corners=12,
                    half_neighbors=(0, 1, 2, 3, 4, 5))
                center = Vector(((2 if row % 2 == 0 else 1) + column * 2, 1 + ((row - 1) * 7 / 4 / 3), 0))
                new_cell.first_vert_index = len(self.verts)
                s_q = size * 0.25 / 2
                s_h = size / 2
                s_tq = size * 0.75 / 2

                self.verts.extend((
                    Vector((s_tq, s_tq, 0)) + center,
                    Vector((s_q, s_h, 0)) + center,
                    Vector((-s_q, s_h, 0)) + center,
                    Vector((-s_tq, s_tq, 0)) + center,
                    Vector((-s_h, s_q, 0)) + center,
                    Vector((-s_h, -s_q, 0)) + center,
                    Vector((-s_tq, -s_tq, 0)) + center,
                    Vector((-s_q, -s_h, 0)) + center,
                    Vector((s_q, -s_h, 0)) + center,
                    Vector((s_tq, -s_tq, 0)) + center,
                    Vector((s_h, -s_q, 0)) + center,
                    Vector((s_h, s_q, 0)) + center))
            return new_cell

    def init_cells_neighbors(self) -> None:
        for c in self.all_cells:
            if (c.row - 1) % 3 == 0:
                c.set_neighbor(1, self.delta_cell(c, 0, 2, 0), 2)
                c.set_neighbor(7, self.delta_cell(c, 0, -2, 0), 2)
                c.set_neighbor(4, self.delta_cell(c, -1, 0, 0), 10)
                if (c.row - 1) % 2 == 0:
                    c.set_neighbor(0, self.delta_cell(c, 0, 3, 0), 6)
                    c.set_neighbor(2, self.delta_cell(c, -1, 3, 0), 8)
                    c.set_neighbor(3, self.delta_cell(c, -1, 1, 0), 1)
                    c.set_neighbor(5, self.delta_cell(c, -1, -1, 0), 0)
                    c.set_neighbor(9, self.delta_cell(c, 0, -1, 0), 1)
                    c.set_neighbor(11, self.delta_cell(c, 0, 1, 0), 0)
                else:
                    c.set_neighbor(0, self.delta_cell(c, 1, 3, 0), 6)
                    c.set_neighbor(2, self.delta_cell(c, 0, 3, 0), 8)
                    c.set_neighbor(3, self.delta_cell(c, 0, 1, 0), 1)
                    c.set_neighbor(5, self.delta_cell(c, 0, -1, 0), 0)
                    c.set_neighbor(9, self.delta_cell(c, 1, -1, 0), 1)
                    c.set_neighbor(11, self.delta_cell(c, 1, 1, 0), 0)


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal: bool = False, weave: int = 0, **kwargs):
        self.use_kruskal = use_kruskal
        self.weave = weave / 100
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
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
        new_cell = CellUnder(cell_over)
        self._cells.append(new_cell)
        self._union_find.data[new_cell] = new_cell
        return new_cell
