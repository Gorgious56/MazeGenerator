"""
Handles data access and modifications relative to a maze's grid
"""

import numpy as np
import operator
from scipy.spatial import Voronoi
import random
from typing import Iterable, Tuple, List, Generator
from mathutils import Vector
from maze_generator.maze.cell.cells import (
    Cell,
    CellOver,  # Keep this.
    CellUnder,  # Keep this.
)
from maze_generator.maze.constants import grid_logic as cst
from maze_generator.helper import (
    union_find,
    event,
    graph,
)
import time


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
        mask: Iterable[Tuple[int]] = None,
        init_cells=True,
        warp_horiz=False,
        warp_vert=False,
        random_cells: int = 0,
    ) -> None:
        self.random_cells = random_cells
        self.shape = (columns, rows, levels)
        self.size = self.shape[0] * self.shape[1] * self.shape[2]
        self.size_2D = self.shape[0] * self.shape[1]
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

        self.new_cell_evt = event.EventHandler(event.Event("New Cell"), self)

        self._union_find = None

        self.warp_horiz = warp_horiz
        self.warp_vert = warp_vert

        self.corners = 4
        self.half_neighbors = (0, 1)

    @property
    def dead_ends_amount(self):
        return len(self.dead_ends)

    def _get_offset(self) -> Vector:
        return Vector(((1 - self.shape[0]) / 2, (1 - self.shape[1]) / 2, 0))

    def mask_cells(self) -> None:
        if self.mask:
            [
                self.mask_patch(
                    mask_patch[0],
                    mask_patch[1],
                    mask_patch[2],
                    mask_patch[3],
                )
                for mask_patch in self.mask
            ]

    def get_neighbor_towards(self, index, direction):
        return abs(self.cells_np[index][direction])

    def get_neighbor_return(self, _index, direction):
        n = self.get_neighbor_towards(_index, direction)
        return index(self.cells_np[n], _index)

    def get_shape_from_index(self, i):
        return (i % self.shape[0], i // self.shape[0])

    def get_cell_position_from_index(self, i):
        return self.get_cell_position_from_shape(self.get_shape_from_index(i))

    def get_cell_position_from_shape(self, shape):
        return Vector((shape[0], shape[1], 0))

    def get_cell_position_2D_from_shape(self, shape):
        if self.random_cells > 0 and 0 < shape[0] < self.shape[0] - 1 and 0 < shape[1] < self.shape[1] - 1:
            # if self.random_cells > 0:
            return (
                round(shape[0] + random.uniform(-0.5, 0.5) * self.random_cells, 2),
                round(shape[1] + random.uniform(-0.5, 0.5) * self.random_cells, 2),
            )
        else:
            return (shape[0], shape[1])

    def get_cell_vertices(self, index):
        size = self.cell_size
        column = index % self.shape[0]
        row = index // self.shape[0]
        center = Vector((column, row, 0))

        verts = (
            center + Vector((size / 2, size / 2, 0)),
            center + Vector((-size / 2, size / 2, 0)),
            center + Vector((-size / 2, -size / 2, 0)),
            center + Vector((size / 2, -size / 2, 0)),
        )
        return verts

    def prepare_grid(self) -> None:
        cols, rows, _ = self.shape
        cells_positions = [
            self.get_cell_position_2D_from_shape(self.get_shape_from_index(idx)) for idx in range(self.size_2D)
        ]

        cells_positions.append(self.get_cell_position_2D_from_shape((-1, -1)))
        for c in range(cols):
            cells_positions.append(self.get_cell_position_2D_from_shape((c, -1)))
        cells_positions.append(self.get_cell_position_2D_from_shape((cols, -1)))
        for r in range(rows):
            cells_positions.append(self.get_cell_position_2D_from_shape((-1, r)))
            cells_positions.append(self.get_cell_position_2D_from_shape((cols, r)))
        cells_positions.append(self.get_cell_position_2D_from_shape((-1, rows)))
        for c in range(cols):
            cells_positions.append(self.get_cell_position_2D_from_shape((c, rows)))
        cells_positions.append(self.get_cell_position_2D_from_shape((cols, rows)))
        print("voronoi")
        start = time.time()
        self.vor = Voronoi(cells_positions, qhull_options="Qc Q3")
        print(time.time() - start)
        not_good_regions = self.vor.point_region[self.size_2D : :]
        self.vor.regions = [r for i, r in enumerate(self.vor.regions) if i not in not_good_regions]
        connections = []
        print("sanitize")
        start = time.time()
        for i in range(len(self.vor.ridge_points) - 1, -1, -1):
            p0, p1 = self.vor.ridge_points[i]
            p1_rim = p0 >= self.size_2D
            p2_rim = p1 >= self.size_2D

            # Do not draw outside cells
            if p1_rim and p2_rim:
                self.vor.ridge_points = np.delete(self.vor.ridge_points, i, 0)
                self.vor.ridge_vertices.pop(i)

            # Remove connections that are too short to make sense
            elif not (p1_rim or p2_rim):
                v0, v1 = self.vor.ridge_vertices[i]
                vec0, vec1 = self.vor.vertices[v0], self.vor.vertices[v1]
                if np.linalg.norm((vec0 - vec1)) > self.cell_size / 6:
                    connections.append((p0, p1))
        print(time.time() - start)

        # print("Points")
        # print(cells_positions)
        # print("Vertices")
        # print(self.vor.vertices)
        # print("Faces")
        # print(self.vor.regions)
        # print("Ridge points")
        # print(self.vor.ridge_points)
        # print("Ridge vertices")
        # print(self.vor.ridge_vertices)
        # print("Connections")
        # print(connections)
        # connections.sort(key=operator.itemgetter(0, 1))
        # print(connections)
        
        print("graph")
        start = time.time()
        self.graph = graph.OrderedGraph(connections=connections)
        print(time.time() - start)

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
        # TODO numpy ?
        return [c for c in self.cells_np if self.has_any_link(c)]

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
            return random.randrange(self.shape[0] * self.shape[1])
        except IndexError:
            return None

    def get_neighbors_array(self, index):
        neighbors = [-1] * 4
        if index < self.shape[0] * (self.shape[1] - 1):
            neighbors[0] = index + self.shape[0]
        if index % self.shape[0] != 0:
            neighbors[1] = index - 1
        if index >= self.shape[0]:
            neighbors[2] = index - self.shape[0]
        if index % self.shape[0] != self.shape[0] - 1:
            neighbors[3] = index + 1
        return neighbors

    def get_neighbors(self, index):
        return list(self.graph.get_neighbors(index))

    def forget_neighbors(self, cell_a, cell_b):
        self.graph.disconnect(cell_a, cell_b)

    def get_random_neighbor(self, index):
        return random.choice(list(self.get_neighbors(index)))

    def has_any_link(self, index):
        return any([self.graph.edge_value(index, n) for n in self.graph.get_neighbors(index)])

    def are_linked(self, cell_a, cell_b):
        return self.graph.connected(cell_a, cell_b) and self.graph.edge_value(cell_a, cell_b)

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
        for level in range(self.levels):
            for r in range(self.rows):
                yield [
                    c
                    for c in self._cells[r * cols + level * self.size_2D : (r + 1) * cols + level * self.size_2D]
                    if c
                ]

    def each_level(self) -> Generator[List[Cell], None, None]:
        """
        Travel the grid level by level, starting at index 0
        """
        for level in range(self.levels):
            yield [c for c in self._cells[level * self.size_2D : (level + 1) * self.size_2D]]

    def each_cell(self) -> Generator[Cell, None, None]:
        for c in (c for c in self._cells if c):
            yield c

    @property
    def all_cells(self) -> List[Cell]:
        return range(0, self.shape[0] * self.shape[1])

    @property
    def all_cells_indices(self) -> List[int]:
        return range(0, self.shape[0] * self.shape[1])

    @property
    def all_cells_with_a_link(self) -> List[Cell]:
        return [c for c in self._cells if c and c.has_any_link()]

    def calc_state(self):
        self.dead_ends = []
        self.max_links_per_cell = 0
        self.groups = set()
        for i, c in enumerate(self.cells_np):
            links = c.sum()
            if links == 1:
                self.dead_ends.append(i)
            self.max_links_per_cell = max(links, self.max_links_per_cell)
            # self.groups.add(c.group)

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
            if not any(self.dead_ends):
                self.dead_ends = [i for i, c in enumerate(self.cells_np) if c.sum() == 1]
                if not any(self.dead_ends):
                    return
            random.shuffle(self.dead_ends)
            while self.dead_ends:
                c = self.dead_ends.pop(0)
                self.unlink(c)
                culled_cells += 1
                if culled_cells >= max_cells_to_cull:
                    return

    def get_neighbor_index(self, cell, neighbor):
        cell_neighbors = self.cells_np[abs(cell)]
        if neighbor not in cell_neighbors:
            neighbor = -neighbor
        return index(cell_neighbors, neighbor)

    def link(self, cell_a, cell_b):
        self.graph.link(cell_a, cell_b)

    def unlink(self, cell_a, cell_b=None):
        if cell_b is None:  # We're unlinking a dead-end
            self.links.remove(cell_a)

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
                neighbors_sorted_by_links = sorted(
                    [n for n in c.neighbors if n not in c.links and n.has_any_link()], key=lambda c: len(c.links)
                )
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

    def get_outer_cells(self):
        if random.random() < 0.5:
            start_cell = self[random.randint(0, self.columns - 1), 0]
            end_cell = self[random.randint(0, self.columns - 1), self.rows - 1]
        else:
            start_cell = self[0, random.randint(0, self.rows - 1)]
            end_cell = self[self.columns - 1, random.randint(0, self.rows - 1)]
        return start_cell, end_cell


def index(array, item):
    return np.where(array == item)[0][0]
