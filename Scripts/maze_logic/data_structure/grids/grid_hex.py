from mathutils import Vector
from .. grids . grid import Grid
from .. cells . cell_hex import CellHex


class GridHex(Grid):
    def __init__(self, rows, columns, name="", cell_size=1):
        super().__init__(rows, columns, name, 'cartesian', sides=6, cell_size=cell_size)

    def prepare_grid(self):
        for r in range(self.rows):
            for c in range(self.columns):
                self[c, r] = CellHex(r, c)

    def configure_cells(self):
        for c in self.each_cell():
            row, col = c.row, c.column

            if col % 2 == 0:
                north_diagonal = row + 1
                south_diagonal = row
            else:
                north_diagonal = row
                south_diagonal = row - 1

            # Neighbor 0 : NE
            c.neighbors[0] = self[col + 1, north_diagonal]
            # Neighbor 1 : N
            c.neighbors[1] = self[col, row + 1]
            # Neighbor 2 : NW
            c.neighbors[2] = self[col - 1, north_diagonal]
            # Neighbor 3 : SW
            c.neighbors[3] = self[col - 1, south_diagonal]
            # Neighbor 4 : S
            c.neighbors[4] = self[col, row - 1]
            # Neighbor 5 : SE
            c.neighbors[5] = self[col + 1, south_diagonal]

    def get_cell_walls(self, c, cell_size=1):
        walls = []
        cells = []
        mask = c.get_wall_mask()
        positions = self.get_cell_position(c, cell_size)
        for i in range(3):
            if mask[i]:
                walls.append(positions[i + 1])
                walls.append(positions[i + 2])
            if self.need_wall_to(c.neighbors[i + 3]):
                walls.append(positions[i + 4])
                walls.append(positions[1 + (i + 4) % 6])
            cells.append(positions[1 + (i * 2)])
            cells.append(positions[2 + (i * 2)])

        return walls, cells, None

    def get_cell_position(self, c, size):
        size /= 2 ** 0.5
        a_size = size / 2
        b_size = size * (3 ** 0.5) / 2
        height = b_size * 2

        center = Vector([size + 3 * c.column * a_size,
                        - b_size * (1 + c.column % 2) + c.row * height,
                        0])

        cx = center.x
        cy = center.y

        x_far_west = cx - size
        x_near_west = cx - a_size
        x_near_east = cx + a_size
        x_far_east = cx + size

        y_north = cy + b_size
        y_mid = cy
        y_south = cy - b_size

        east = (x_far_east, y_mid, 0)
        north_east = (x_near_east, y_north, 0)
        north_west = (x_near_west, y_north, 0)
        west = (x_far_west, y_mid, 0)
        south_west = (x_near_west, y_south, 0)
        south_east = (x_near_east, y_south, 0)
        return center, east, north_east, north_west, west, south_west, south_east
