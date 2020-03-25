from mathutils import Vector
from . grid import Grid
from .. cells . cell_under import CellUnder
from .. cells . cell_over import CellOver


class GridWeave(Grid):
    def __init__(self, cell_thickness=0, *args, **kwargs):
        self.cells_under = []
        super().__init__(*args, **kwargs)
        self.cell_thickness = cell_thickness

    def prepare_grid(self):
        for c in range(self.columns):
            for r in range(self.rows):
                self[c, r] = CellOver(row=r, col=c, grid=self)

    def tunnel_under(self, cell_over):
        self.cells_under.append(CellUnder(cell_over))

    def each_cell(self):
        for c in super().each_cell():
            yield c

        for cu in self.cells_under:
            yield cu

    def get_cell_walls(self, c):
        cell_visual = super().get_cell_walls(c)
        delta_z = self.cell_thickness + 0.05
        if type(c) is CellUnder:
            cell_visual.walls = []
            for f in cell_visual.faces:
                if f.connection:
                    f.vertices[0] -= Vector([0, 0, delta_z])
                    f.vertices[3] -= Vector([0, 0, delta_z])
                else:
                    for v in f.vertices:
                        v -= Vector([0, 0, delta_z])
        return cell_visual
