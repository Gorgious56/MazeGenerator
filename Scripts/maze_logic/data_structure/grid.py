from . import cell
from math import pi
from mathutils import Vector, Matrix
from random import choice, seed, shuffle


class Grid:
    def __init__(self, rows, columns, name="", coord_system='cartesian', sides=4):
        self.rows = rows
        self.columns = columns
        self.cells = [None] * (rows * columns)
        self.size = rows * columns
        self.masked_cells = []
        self.name = name

        self.coord_system = coord_system

        self.sides_per_cell = sides

        self.prepare_grid()
        self.configure_cells()

        self.offset = (columns / 2, rows / 2, 0)

    def __delitem__(self, key):
        del self.cells[key[0] + key[1] * self.columns]

    def __getitem__(self, key):
        return self.cells[key[0] + key[1] * self.columns] \
            if (self.columns > key[0] >= 0 and self.rows > key[1] >= 0) else None

    def __setitem__(self, key, value):
        self.cells[key[0] + key[1] * self.columns] = value

    def prepare_grid(self):
        for c in range(self.columns):
            for r in range(self.rows):
                self[c, r] = cell.Cell(r, c)

    def configure_cells(self):
        for c in self.cells:
            row, col = c.row, c.column

            # North :
            c.neighbors[0] = self[col, row + 1]
            # West :
            c.neighbors[1] = self[col - 1, row]
            # South :
            c.neighbors[2] = self[col, row - 1]
            # East :
            c.neighbors[3] = self[col + 1, row]

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            seed(_seed)
        try:
            return choice(self.get_unmasked_cells()) if filter_mask else choice(self.cells)
        except IndexError:
            return None

    def get_random_unmasked_and_linked_cell(self, _seed=None):
        if _seed:
            seed(_seed)
        try:
            return choice(self.get_unmasked_and_linked_cells())
        except IndexError:
            return None

    def each_row(self):
        cols = self.columns
        for r in range(self.rows):
            yield [c for c in self.cells[r * cols: (r + 1) * cols] if not c.is_masked]

    def each_column(self):
        cols = self.columns
        for c in range(cols):
            yield [self.cells[r * cols + c] for r in range(self.rows) if not self.cells[r * cols + c].is_masked]

    def each_cell(self):
        for c in self.get_unmasked_cells():
            yield c

    def get_dead_ends(self):
        return [c for c in self.get_unmasked_cells() if len(c.links) == 1]

    def braid_dead_ends(self, braid=0):
        if braid > 0:
            dead_ends_shuffle = self.get_dead_ends()
            shuffle(dead_ends_shuffle)
            stop_index = int(len(dead_ends_shuffle) * min(max(0, braid), 1))
            for c in dead_ends_shuffle[0:stop_index]:
                if len(c.links) != 1:
                    pass
                else:
                    unconnected_neighbors = [_c for _c in c.get_neighbors() if _c not in c.links]
                    if len(unconnected_neighbors) > 0:
                        best = [_c for _c in unconnected_neighbors if len(c.links) < 2]
                        if len(best) == 0:
                            best = unconnected_neighbors
                        c.link(choice(best))
            return dead_ends_shuffle[stop_index:len(dead_ends_shuffle)]
        else:
            return None

    def mask_cell(self, column, row):
        c = self[column, row]
        if c is not None:
            c.is_masked = True
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None

    def mask_ring(self, center_row, center_col, radius):
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

    def get_unmasked_cells(self):
        return [c for c in self.cells if not c.is_masked]



    def get_unmasked_and_linked_cells(self):
        return [c for c in self.each_cell() if any(c.links)]

    def is_cell_linked(self, c):
        return c and any(c.links)

    def get_cell_position(self, c, cell_size=1):
        # center = Vector([c.column * cell_size, c.row * cell_size, 0]) - offset
        # top_left = Vector([(c.column - 0.5) * cell_size, (c.row + 0.5) * cell_size, 0]) - offset
        # top_right = Vector([(c.column + 0.5) * cell_size, (c.row + 0.5) * cell_size, 0]) - offset
        # bot_right = Vector([(c.column + 0.5) * cell_size, (c.row - 0.5) * cell_size, 0]) - offset
        # bot_left = Vector([(c.column - 0.5) * cell_size, (c.row - 0.5) * cell_size, 0]) - offset
        center = (c.column * cell_size, c.row * cell_size, 0)
        top_left = ((c.column - 0.5) * cell_size, (c.row + 0.5) * cell_size, 0)
        top_right = ((c.column + 0.5) * cell_size, (c.row + 0.5) * cell_size, 0)
        bot_right = ((c.column + 0.5) * cell_size, (c.row - 0.5) * cell_size, 0)
        bot_left = ((c.column - 0.5) * cell_size, (c.row - 0.5) * cell_size, 0)
        # center = self.sub_vec((c.column * cell_size, c.row * cell_size, 0), offset)
        # top_left = self.sub_vec(((c.column - 0.5) * cell_size, (c.row + 0.5) * cell_size, 0), offset)
        # top_right = self.sub_vec(((c.column + 0.5) * cell_size, (c.row + 0.5) * cell_size, 0), offset)
        # bot_right = self.sub_vec(((c.column + 0.5) * cell_size, (c.row - 0.5) * cell_size, 0), offset)
        # bot_left = self.sub_vec(((c.column - 0.5) * cell_size, (c.row - 0.5) * cell_size, 0), offset)
        return center, top_left, top_right, bot_right, bot_left

    def sub_vec(self, vec1, vec2):
        return (vec1[0] - vec2[0], vec1[1] - vec2[1], vec1[2] - vec2[2])

    def get_cell_rotation(self, c):
        return Vector([0, 0, 45])

    def get_blueprint(self):
        walls = []
        cells = []
        for c in self.get_unmasked_and_linked_cells():
            new_walls, new_cells = self.get_cell_walls(c)
            walls.extend(new_walls)
            cells.extend(new_cells)
        return walls, cells

    def get_matrix(self, c):
        return Matrix.Translation((c.column, c.row, 0)) @ Matrix.Rotation(-pi/4,4,"Z")

    def need_wall_to(self, c):
        return not c or c.is_masked or not c.has_any_link()

    def get_cell_walls(self, c, cell_size=1):
        walls = []
        cells = []
        mask = c.get_wall_mask()
        positions = self.get_cell_position(c, cell_size)
        if mask[0]:
            walls.append(positions[1])
            walls.append(positions[2])
        if mask[3]:
            walls.append(positions[2])
            walls.append(positions[3])
        if self.need_wall_to(c.neighbors[2]):
            walls.append(positions[3])
            walls.append(positions[4])
        if self.need_wall_to(c.neighbors[1]):
            walls.append(positions[1])
            walls.append(positions[4])

        cells.append(positions[1])
        cells.append(positions[2])
        cells.append(positions[3])
        cells.append(positions[4])
        
        return walls, cells
