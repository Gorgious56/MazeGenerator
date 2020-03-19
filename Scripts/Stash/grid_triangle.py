from mathutils import Vector
import grid
import cell_triangle

class GridTriangle(grid.Grid):
    def __init__(self, rows, columns, name=""):
        super().__init__(rows, columns, name, 'cartesian', sides=3)   

    def prepare_grid(self):
        for r in range(self.rows):
            for c in range(self.columns):
                self[c, r] = cell_triangle.CellTriangle(r,c)

    def configure_cells(self):
        for c in self.each_cell():
            row, col = c.row, c.column

            if c.is_upright():
                # NE
                c.neighbors[0] = self[col + 1, row]
                # NW
                c.neighbors[1] = self[col - 1, row]
                # S
                c.neighbors[2] = self[col , row - 1]
            else:
                # SW
                c.neighbors[0] = self[col - 1, row]
                # SE
                c.neighbors[1] = self[col + 1, row]
                # N
                c.neighbors[2] = self[col, row + 1]

    def get_cell_position(self, c, size, offset):
        width = size
        half_width = width / 2

        height = size * (3 ** 0.5) / 2
        half_height = height / 2

        cx = half_width + c.column * half_width
        cy = half_height + c.row * height

        west_x = cx - half_width
        mid_x = cx
        east_x = cx + half_width

        if c.is_upright():
            base_y = cy + half_height
            apex_y = cy - half_height
        else:            
            base_y = cy - half_height
            apex_y = cy + half_height

        center = Vector([size * c.column * (3 ** 0.5) / 2,
                        size * (c.row  * 1.5 + (0 if c.is_upright() else 0.5)),
                        0]) - offset
        
        # TODO Rewrite for hex
        top_left = Vector([(c.column - 0.5) * size, (c.row + 0.5) * size, 0]) - offset
        top_right = Vector([(c.column + 0.5) * size, (c.row + 0.5) * size, 0]) - offset
        bot_right = Vector([(c.column + 0.5) * size, (c.row - 0.5) * size, 0]) - offset
        bot_left = Vector([(c.column - 0.5) * size, (c.row - 0.5) * size, 0]) - offset
        return center, top_left, top_right, bot_right, bot_left
    
    def get_cell_rotation(self, c):
        return Vector([0, 0, -30 if c.is_upright() else 150]) 