import random
from typing import Iterable, Tuple, List, Generator
from mathutils import Vector
from math import pi, floor, cos, sin
from .cells import Cell, CellHex, CellOver, CellPolar, CellTriangle, CellUnder
from ..managers import space_rep_manager as sp_mgr
# from ..managers.mesh_manager import VG_DISPLACE
from . import constants as cst
from ..managers.distance_manager import Distances
from ..utils import event, union_find


class Grid:
    CELL_TYPE = Cell

    def __init__(self, rows: int = 2, columns: int = 2, levels: int = 1, cell_size: int = 1, space_rep: int = 0, mask: Iterable[Tuple[int]] = None) -> None:
        self.rows: int = rows
        self.columns = columns
        self.levels = levels

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

        self.verts_indices = {}
        self.new_cell_evt = event.EventHandler(event.Event('New Cell'), self)

        self._union_find = None

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

    def prepare_grid(self) -> None:
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = self.CELL_TYPE(r, c, l) if self[c, r, l] is None else None
                    self.new_cell_evt(self[c, r, l])

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
            self.masked_cells += 1
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

    def braid_dead_ends(self, braid: int = 0, _seed: int = None) -> int:
        """
        This will link each dead-end to a neighboring cell
        The method will favor other neighboring dead-ends to link to

        braid : Amount between 0 (no braid) and 100 (all dead-ends are braided)

        Returns the number of dead-ends after braiding
        """
        dead_ends_shuffle = self.dead_ends.copy()
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
                            self.dead_ends.remove(best)
                        else:
                            best = unconnected_neighbors
                        self.link(c, random.choice(best))
                        self.dead_ends.remove(c)

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
            random.shuffle(dead_ends)
            for c in dead_ends:
                try:
                    c.unlink(next(iter(c.links)))
                    culled_cells += 1
                    if culled_cells >= max_cells_to_cull:                     
                        self.dead_ends.remove(c)
                        return
                except (StopIteration, AttributeError):
                    self.dead_ends.remove(c)
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
        1 0
        2 3
        """
        size = self.cell_size
        center = self.get_cell_center(cell)
        return center + Vector(((size / 2), (size / 2), 0)), center + Vector(((-size / 2), (size / 2), 0)), center + Vector(((-size / 2), (-size / 2), 0)), center + Vector(((size / 2), (-size / 2), 0))

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

    def link(self, cell_a, cell_b, bidirectional=True):
        linked_cells = cell_a.link(cell_b, bidirectional)
        if linked_cells and all(linked_cells):
            self._union_find.union(linked_cells[0], linked_cells[1])
        return linked_cells

    def unlink(self, cell_a, cell_b):
        cell_a.unlink(cell_b)


class GridHex(Grid):
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

    def get_cell_center(self, c):
        return Vector([1 + 3 * c.column / 2, - (3 ** 0.5) * ((1 + c.column % 2) / 2 - c.row), 0])

    def get_cell_positions(self, cell):
        size = self.cell_size
        center = self.get_cell_center(cell)
        a_size = size / 2
        b_size = size * (3 ** 0.5) / 2

        east = Vector((size, 0, 0)) + center
        north_east = Vector((a_size, b_size, 0)) + center
        north_west = Vector((-a_size, b_size, 0)) + center
        west = Vector((- size, 0, 0)) + center
        south_west = Vector((-a_size, -b_size, 0)) + center
        south_east = Vector((a_size, -b_size, 0)) + center
        return east, north_east, north_west, west, south_west, south_east


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
        key = list(key)
        try:
            row = self.rows_polar[key[0]]
            if key[1] == len(row):
                key[1] = 0
            elif key[1] == -1:
                key[1] = len(row) - 1
            return row[key[1]]
        except IndexError:
            return None

    def __setitem__(self, key, value):
        try:
            row = self.rows_polar[key[0]]
            if key[1] == len(row):
                key[1] = 0
            elif key[1] == -1:
                key[1] = len(row) - 1
            row[key[1]] = value
        except IndexError:
            pass

    def delta_cell(self, cell: Cell, column: int = 0, row: int = 0, level: int = 0) -> Cell:
        if not cell:
            return
        if column == -1:
            if cell.row == 0:
            return random.choice(cell.neighbors)
        else:
            return self[cell.row, cell.column - 1]
        elif column == 1:
            if cell.row == 0:
            return random.choice(cell.neighbors)
        else:
            return self[cell.row, cell.column + 1]
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
        return len(self.rows_polar[row])

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
        # 0>ccw - 1>in - 2>cw - 3...>outward
        all_cells = self.all_cells
        for c in all_cells:
            row, col = c.row, c.column
            if row > 0:
                row_length = self.row_length(c.row)
                c.set_neighbor(cst.POL_CCW, self.delta_cell(c, column=1))
                c.set_neighbor(cst.POL_CW, self.delta_cell(c, column=-1))

                ratio = row_length / self.row_length(c.row - 1)
                parent = self[row - 1, floor(col // ratio)]

                c.set_neighbor(cst.POL_IN, parent)

        for cell in all_cells:
            self.new_cell_evt(cell)

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

    def random_cell(self, _seed=None):
        if _seed:
            random.seed(_seed)
        return random.choice([c for c in random.choice(self.rows_polar)])

    def row_length(self, row):
        return len(self.rows_polar[row])

    def get_cell_positions(self, cell):
        cs = self.cell_size
        cell_corners = cell.corners
        if cell.row == 0:
            a_size = cs / 2
            b_size = cs * (3 ** 0.5) / 2
            return Vector((cs, 0, 0)), Vector((a_size, b_size, 0)), Vector((-a_size, b_size, 0)), Vector((-cs, 0, 0)), Vector((-a_size, -b_size, 0)), Vector((a_size, -b_size, 0))

        def get_position(radius, angle):
            return Vector((radius * cos(angle), radius * sin(angle), 0))

        row_length = self.row_length(cell.row)
        t = 2 * pi / row_length
        r_in = cell.row + 0.5 - cs / 2
        r_out = r_in + cs
        t_cw = (cell.column + 0.5 - cs / 2) * t
        t_ccw = t_cw + cs * t

        r_in_cw = get_position(r_in, t_cw)
        r_out_cw = get_position(r_out, t_cw)
        r_in_ccw = get_position(r_in, t_ccw)
        r_out_ccw = get_position(r_out, t_ccw)
        return (r_out_ccw, r_in_ccw, r_in_cw, r_out_cw, get_position(r_out, (2 * cell.column + 1) * 2 * pi / self.row_length(cell.row + 1))) if cell_corners == 5 else (r_out_ccw, r_in_ccw, r_in_cw, r_out_cw)

    def _get_offset(self) -> Vector:
        return Vector((0, 0, 0))


class GridTriangle(Grid):
    CELL_TYPE = CellTriangle

    def init_cells_neighbors(self) -> None:
        for c in self.each_cell():
            if c.is_upright():
                c.set_neighbor(0, self.delta_cell(c, row=1))
                c.set_neighbor(1, self.delta_cell(c, column=-1))
                c.set_neighbor(2, self.delta_cell(c, row=-1))

    def _get_offset(self) -> Vector:
        return Vector((-self.columns / 4, -self.rows / 3, 0))

    def get_cell_center(self, c):
        return Vector((c.column * 0.5, c.row * (3 ** 0.5) / 2, 0))

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
        return (east, north_or_south, west) if cell.is_upright() else (west, north_or_south, east)


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
        new_cell = CellUnder(cell_over)
        self._cells.append(new_cell)
        self._union_find.data[new_cell] = new_cell
        return new_cell
