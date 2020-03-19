from mathutils import Vector
import grid
import cell_hex

class GridHex(grid.Grid):
    def __init__(self, rows, columns, name=""):
        super().__init__(rows, columns, name, 'cartesian', sides=6)   

    def prepare_grid(self):
        for r in range(self.rows):
            for c in range(self.columns):
                self[c, r] = cell_hex.CellHex(r,c)

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


    def get_cell_position(self, c, size, offset):
        size /= 2 ** 0.5        
        a_size = size / 2
        b_size = size * (3 ** 0.5) / 2
        width = size * 2
        height = b_size * 2

        center = Vector([size + 3 * c.column * a_size,
                        - b_size * (1 + c.column % 2) + c.row * height,
                        0]) - offset
        
        # TODO Rewrite for hex
        top_left = Vector([(c.column - 0.5) * size, (c.row + 0.5) * size, 0]) - offset
        top_right = Vector([(c.column + 0.5) * size, (c.row + 0.5) * size, 0]) - offset
        bot_right = Vector([(c.column + 0.5) * size, (c.row - 0.5) * size, 0]) - offset
        bot_left = Vector([(c.column - 0.5) * size, (c.row - 0.5) * size, 0]) - offset
        return center, top_left, top_right, bot_right, bot_left
    
    def get_cell_rotation(self, c):
        return Vector([0, 0, 0])