from . grid import Grid
from .. cell import CellUnder, CellOver, Cell
from .... visual . cell_visual import DISPLACE


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal=False, weave=0, **kwargs):
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
                self[c, r] = CellOver(row=r, col=c)
                self[c, r].request_tunnel_under += lambda cell, neighbor: self.tunnel_under(neighbor)
    """
    Tunnel under the specified cell of type 'CellOver'
    Returns the resulting 'CellUnder'
    """
    def tunnel_under(self, cell_over):
        self._cells.append(CellUnder(cell_over))
        return self._cells[-1]

    def get_cell_walls(self, c):
        cv = super().get_cell_walls(c)
        if type(c) is CellUnder:
            cv.walls = []
            for f in cv.faces:
                f.set_vertex_group(DISPLACE, [v_level for v_level in f.vertices_levels])
        return cv
