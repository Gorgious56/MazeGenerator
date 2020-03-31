from mathutils import Vector
from .. grids . grid import Grid, CellVisual
from .. cell import CellTriangle


class GridTriangle(Grid):
    def __init__(self, rows, columns, levels, cell_size, space_rep, mask=None):
        super().__init__(rows, columns, levels, cell_size, space_rep, mask)
        self.offset = Vector((-self.columns / 4, -self.rows / 3, 0))

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

    def get_cell_walls(self, c):
        cv = CellVisual(c)
        center, north_or_south, west, east = self.get_cell_position(c)
        cs = self.cell_size

        if self.cell_size == 1:
            if c.is_upright():
                if not c.exists_and_is_linked_neighbor_index(0):
                    cv.create_wall(north_or_south, east)
                if not c.exists_and_is_linked_neighbor_index(1):
                    cv.create_wall(north_or_south, west)
                if not c.exists_and_is_linked_neighbor_index(2):
                    cv.create_wall(west, east)
            else:
                if not c.exists_and_is_linked_neighbor_index(0):
                    cv.create_wall(north_or_south, west)
                if not c.exists_and_is_linked_neighbor_index(1):
                    cv.create_wall(north_or_south, east)
                if not c.exists_and_is_linked_neighbor_index(2):
                    cv.create_wall(west, east)
            if c.is_upright():
                cv.add_face((east, north_or_south, west))
            else:
                cv.add_face((east, west, north_or_south))
        else:            
            horiz_left = west + (east - west) * (0.5 - (cs / 2))
            horiz_right = west + (east - west) * (0.5 + (cs / 2))

            _, north_or_south_b, west_b, east_b = self.get_cell_position(c, size=self.cell_size)

            if c.is_upright():
                nw_bot = west + (north_or_south - west) * (0.5 - (cs / 2))
                nw_top = west + (north_or_south - west) * (0.5 + (cs / 2))
                ne_bot = east + (north_or_south - east) * (0.5 - (cs / 2))
                ne_top = east + (north_or_south - east) * (0.5 + (cs / 2))
                cv.add_face((east_b, north_or_south_b, west_b))
                if c.exists_and_is_linked_neighbor_index(0):
                    cv.add_face((north_or_south_b, east_b, ne_bot, ne_top))
                if c.exists_and_is_linked_neighbor_index(1):
                    cv.add_face((north_or_south_b, nw_top, nw_bot, west_b))
                if c.exists_and_is_linked_neighbor_index(2):
                    cv.add_face((west_b, horiz_left, horiz_right, east_b))
            else:
                nw_bot = north_or_south + (west - north_or_south) * (0.5 - (cs / 2))
                nw_top = north_or_south + (west - north_or_south) * (0.5 + (cs / 2))
                ne_bot = north_or_south + (east - north_or_south) * (0.5 - (cs / 2))
                ne_top = north_or_south + (east - north_or_south) * (0.5 + (cs / 2))
                cv.add_face((west_b, north_or_south_b, east_b))    
                if c.exists_and_is_linked_neighbor_index(0):
                    cv.add_face((west_b, nw_top, nw_bot, north_or_south_b))
                if c.exists_and_is_linked_neighbor_index(1):
                    cv.add_face((north_or_south_b, ne_bot, ne_top, east_b))
                if c.exists_and_is_linked_neighbor_index(2):
                    cv.add_face((east_b, horiz_right, horiz_left, west_b))            

        return cv

    def get_cell_position(self, c, size=1):
        width = size
        half_width = width / 2

        height = size * (3 ** 0.5) / 2
        half_height = height / 2

        center = Vector((c.column * 0.5, c.row * (3 ** 0.5) / 2, 0)) + self.offset
        
        cx = center.x
        cy = center.y

        west_x = cx - half_width
        mid_x = cx
        east_x = cx + half_width

        if c.is_upright():
            base_y = cy - half_height
            apex_y = cy + half_height

        else:
            base_y = cy + half_height
            apex_y = cy - half_height
                
        north_or_south = Vector((mid_x, apex_y, 0))
        west = Vector((west_x, base_y, 0))
        east = Vector((east_x, base_y, 0))
        
        return center, north_or_south, west, east
