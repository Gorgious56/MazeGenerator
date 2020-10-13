"""
Weave Grid
"""


from ..cells import Cell, CellOver, CellUnder
from .grid import Grid


class GridWeave(Grid):
    """
    Weave Grid
    """

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
                    self[c, r, l] = CellOver(
                        r, c, l) if self[c, r, l] is None else None
                    self[c, r, l].request_tunnel_under += lambda cell, neighbor: self.tunnel_under(
                        neighbor)

    def tunnel_under(self, cell_over):
        """
        Tunnel under the specified cell of type 'CellOver'

        Returns the resulting 'CellUnder'
        """
        new_cell = CellUnder(cell_over)
        self._cells.append(new_cell)
        self._union_find.data[new_cell] = new_cell
        return new_cell
