"""
Handles data access and modifications relative to a maze's grid
"""


import random
from typing import Iterable, Tuple, List, Generator
from mathutils import Vector
from ..cells import Cell
from .. import constants as cst
from ..distance import Distances
from ...utils import event, union_find


class Grid:
    """
    Handles data access and modifications relative to a maze's grid
    """

    def __init__(
            self, 
            rows: int = 2, 
            columns: int = 2, 
            levels: int = 1, 
            cell_size: float = 1.0, 
            # space_rep: int = 0, 
            mask: Iterable[Tuple[int]] = None, 
            init_cells=True,
            warp_horiz=False,
            warp_vert=False) -> None:
        self.rows: int = rows
        self.columns = columns
        self.levels = levels
        if init_cells:
            self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = 0  # This container is used in some algorithms.
        # self.space_rep = space_rep

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

        self.warp_horiz = warp_horiz
        self.warp_vert = warp_vert

    def __delitem__(self, key):
        del self._cells[key[0] + key[1] * self.columns]

    def __getitem__(self, key):        
        key = list(key)
        if len(key) == 2:
            key.append(0)
        if self.warp_horiz:
            if key[0] == -1:
                key[0] = self.columns - 1
            elif key[0] == self.columns:
                key[0] = 0
            if self.warp_vert:
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
            self._cells[key[0] + key[1] * self.columns +
                        key[2] * self.size_2D] = value

    def _get_offset(self) -> Vector:
        return Vector(((1 - self.columns) / 2, (1 - self.rows) / 2, 0))

    def mask_cells(self) -> None:
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2],
                             mask_patch[3],) for mask_patch in self.mask]

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
        for c in self.all_cells:
            c.set_neighbor(cst.NORTH, self.delta_cell(c, row=1), cst.SOUTH)
            c.set_neighbor(cst.EAST, self.delta_cell(
                c, column=1), cst.WEST)
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
            self.dead_ends = [
                c for c in self.all_cells if c and len(c.links) == 1]
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
            self.dead_ends = [
                c for c in self.all_cells if c and len(c.links) == 1]
            braid /= 100
            random.seed(_seed)
            dead_ends_to_keep = int(
                len(self.dead_ends) * min(max(0, 1 - braid), 1))
            random.shuffle(self.dead_ends)
            while self.dead_ends and len(self.dead_ends) >= dead_ends_to_keep:
                c = self.dead_ends[0]
                neighbors_sorted_by_links = sorted(
                    [n for n in c.neighbors if n not in c.links and n.has_any_link()], key=lambda c: len(c.links))
                if neighbors_sorted_by_links:
                    best_neighbor = neighbors_sorted_by_links[0]
                    self.link(c, best_neighbor)
                    self.max_links_per_cell = max(len(c.links), len(
                        best_neighbor.links), self.max_links_per_cell)
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
        if props.path.solution == 'Random':                    
            if props.path.force_outside:
                if random.random() < .5:
                    start_cell = self[random.randint(0, self.columns - 1), 0]
                    end_cell = self[random.randint(
                        0, self.columns - 1), self.rows - 1]
                else:
                    start_cell = self[0, random.randint(0, self.rows - 1)]
                    end_cell = self[self.columns - 1,
                                    random.randint(0, self.rows - 1)]
            else:
                    start_cell = self[
                        random.randint(0, self.columns - 1), 
                        random.randint(0, self.rows - 1)]
                    end_cell = self[
                        random.randint(0, self.columns - 1), 
                        random.randint(0, self.rows - 1)]
            setattr(self, "start_cell", start_cell)
            setattr(self, "end_cell", end_cell)
            self.distances = Distances(start_cell)
            self.longest_path = self.distances.path_to(end_cell).path
        elif props.path.solution == 'Custom': 
            start_cell = self[
                min(props.path.start[0], self.columns - 1), 
                min(props.path.start[1], self.rows - 1)]
            end_cell = self[
                min(props.path.end[0], self.columns - 1), 
                min(props.path.end[1], self.rows - 1)]
            setattr(self, "start_cell", start_cell)
            setattr(self, "end_cell", end_cell)
            self.distances = Distances(start_cell)
            self.longest_path = self.distances.path_to(end_cell).path
        else: # Longest path possible
            distances = Distances(self.get_random_linked_cell(_seed=props.seed))
            new_start, distance = distances.max
            distances = Distances(new_start)
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
