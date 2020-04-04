from . grid import Grid
from .. cell import CellUnder, CellOver, Cell
from .... visual . cell_visual import DISPLACE


class GridWeave(Grid):
    def __init__(self, *args, use_kruskal=False, weave=0, **kwargs):
        self.use_kruskal = use_kruskal
        self.weave = weave / 100
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        if self.use_kruskal:
            CellOver.get_neighbors = Cell.get_neighbors
        else:
            CellOver.get_neighbors = CellOver.get_neighbors_copy

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = CellOver(r, c, l) if self[c, r, l] is None else None
                    self[c, r, l].request_tunnel_under += lambda cell, neighbor: self.tunnel_under(neighbor)
    """
    Tunnel under the specified cell of type 'CellOver'
    Returns the resulting 'CellUnder'
    """
    def tunnel_under(self, cell_over):
        self._cells.append(CellUnder(cell_over))
        return self._cells[-1]

    def set_cell_visuals(self, c):
        cv = super().set_cell_visuals(c)
        if type(c) is CellUnder:
            cv.walls = []
            for f in cv.faces:
                f.set_vertex_group(DISPLACE, [v_level for v_level in f.vertices_levels])
        return cv
