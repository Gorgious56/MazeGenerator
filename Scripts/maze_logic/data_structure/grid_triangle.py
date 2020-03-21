from mathutils import Vector
from . grid import Grid
from . cell_triangle import CellTriangle


class GridTriangle(Grid):
    def __init__(self, rows, columns, name=""):
        super().__init__(rows, columns, name, 'cartesian', sides=3)

    def prepare_grid(self):
        for r in range(self.rows):
            for c in range(self.columns):
                self[c, r] = CellTriangle(r, c)

    def configure_cells(self):
        for c in self.each_cell():
            row, col = c.row, c.column

            if c.is_upright():
                # NE
                c.neighbors[0] = self[col + 1, row]
                # NW
                c.neighbors[1] = self[col - 1, row]
                # S
                c.neighbors[2] = self[col, row - 1]
            else:
                # SW
                c.neighbors[0] = self[col - 1, row]
                # SE
                c.neighbors[1] = self[col + 1, row]
                # N
                c.neighbors[2] = self[col, row + 1]

    def get_cell_walls(self, c, cell_size=1):
        walls = []
        cells = []
        mask = c.get_wall_mask()
        positions = self.get_cell_position(c, cell_size)

        if c.is_upright():
            if not c.exists_and_is_linked_neighbor_index(0):
                #c
                walls.append(positions[1])
                walls.append(positions[3])
            if not c.exists_and_is_linked_neighbor_index(1):
                #b
                walls.append(positions[1])
                walls.append(positions[2])
            if not c.exists_and_is_linked_neighbor_index(2):
                #a
                walls.append(positions[2])
                walls.append(positions[3])
        else:
            if not c.exists_and_is_linked_neighbor_index(0):
                #b
                walls.append(positions[1])
                walls.append(positions[2])   
            if not c.exists_and_is_linked_neighbor_index(1):   
                #c
                walls.append(positions[1])
                walls.append(positions[3]) 
            if not c.exists_and_is_linked_neighbor_index(2):  
                #a
                walls.append(positions[2])
                walls.append(positions[3])
        cells.append(positions[3])
        cells.append(positions[1])
        cells.append(positions[2])  
      
        return walls, cells

    def get_cell_position(self, c, size):
        width = size
        half_width = width / 2

        height = size * (3 ** 0.5) / 2
        half_height = height / 2

        center = Vector([size * c.column * 0.5, size * (c.row * (3 ** 0.5) / 2), 0])
        
        # cx = half_width + c.column * half_width
        # cy = half_height + c.row * height
        cx = center.x
        cy = center.y

        west_x = cx - half_width
        mid_x = cx
        east_x = cx + half_width

        if not c.is_upright():
            base_y = cy + half_height
            apex_y = cy - half_height
        else:
            base_y = cy - half_height
            apex_y = cy + half_height
                
        north_or_south = (mid_x, apex_y, 0)
        west = (west_x, base_y, 0)
        east = (east_x, base_y, 0)
        return center, north_or_south, west, east
