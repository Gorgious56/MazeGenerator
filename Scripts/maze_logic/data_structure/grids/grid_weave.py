from random import random, shuffle
from . grid import Grid
from .. cell import CellUnder, CellOver, Cell
from .... visual . cell_visual_manager import DISPLACE


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal=False, weave=0, **kwargs):
        # self.cells_under = {}
        self.cells_under = []
        self.use_kruskal = use_kruskal
        self.weave = weave / 100
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
        if self.use_kruskal:
            CellOver.get_neighbors = Cell.get_neighbors
        else:
            CellOver.get_neighbors = CellOver.get_neighbors_copy

        for c in range(self.columns):
            for r in range(self.rows):
                self[c, r] = CellOver(row=r, col=c, grid=self)

    def tunnel_under(self, cell_over):
        # self.cells_under[cell_over] = CellUnder(cell_over)
        self.cells_under.append(CellUnder(cell_over))

    def all_cells(self):
        all_cells = super().all_cells()
        all_cells.extend(self.cells_under)
        return all_cells

    def each_cell(self):
        for c in super().each_cell():
            yield c

        # for co, cu in self.cells_under.items():
        for cu in self.cells_under:
            yield cu

    def get_cell_walls(self, c):
        cv = super().get_cell_walls(c)
        if type(c) is CellUnder:
            cv.walls = []
            for f in cv.faces:
                f.set_vertex_group(DISPLACE, [v_level for v_level in f.vertices_levels])
        return cv
