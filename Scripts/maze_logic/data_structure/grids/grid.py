from .. cells import cell
from random import choice, seed, shuffle
from mathutils import Vector

TOP = 'TOP'
BOT = 'BOT'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
TOP_BORDER = 'TOP_BORDER'
BOT_BORDER = 'BOT_BORDER'
LEFT_BORDER = 'LEFT_BORDER'
RIGHT_BORDER = 'RIGHT_BORDER'


class Grid:
    def __init__(self, rows, columns, name="", coord_system='cartesian', sides=4, cell_size=1):
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

        self.cell_size = cell_size

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

    def braid_dead_ends(self, braid=0, _seed=None):
        dead_ends_shuffle = self.get_dead_ends()
        dead_ends = len(dead_ends_shuffle)
        if braid > 0:
            braid /= 100
            seed(_seed)

            shuffle(dead_ends_shuffle)
            stop_index = int(len(dead_ends_shuffle) * min(max(0, braid), 1))
            for c in dead_ends_shuffle[0:stop_index]:
                if len(c.links) == 1:
                    unconnected_neighbors = [_c for _c in c.get_neighbors() if _c not in c.links and _c.has_any_link()]
                    if len(unconnected_neighbors) > 0:
                        best = [_c for _c in unconnected_neighbors if len(c.links) < 2]
                        if len(best) == 0:
                            best = unconnected_neighbors
                        c.link(choice(best))
                        dead_ends -= 1
        return dead_ends

    def sparse_dead_ends(self, sparse=0, braid=0, _seed=None):
        max_cells_to_cull = len(self.get_unmasked_and_linked_cells()) * (sparse / 100) - 2
        culled_cells = 0
        while culled_cells < max_cells_to_cull:
            dead_ends = self.get_dead_ends()
            if not any(dead_ends):
                return
            for c in dead_ends:
                try:
                    c.unlink(next(iter(c.links)))
                    culled_cells += 1
                    if culled_cells >= max_cells_to_cull:
                        return
                except StopIteration:
                    return

    def cull_dead_ends(self, culled_cells):
        for c in self.get_dead_ends():
            for i, n in enumerate(c.get_neighbors()):
                c.unlink(n)

    def mask_cell(self, column, row):
        c = self[column, row]
        if c is not None:
            c.is_masked = True
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None
                c.unlink(n)

    def mask_ring(self, center_row, center_col, radius):
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

    def get_unmasked_cells(self):
        return [c for c in self.cells if not c.is_masked]

    def get_unmasked_and_linked_cells(self):
        return [c for c in self.each_cell() if any(c.links)]

    def get_cell_position(self, c):
        positions = {}
        cell_size = self.cell_size
        border = (1 - cell_size) / 2
        positions['center'] = Vector([c.column, c.row, 0])
        positions['top_left'] = Vector([c.column - 0.5, c.row + 0.5, 0])
        positions['top_right'] = Vector([c.column + 0.5, c.row + 0.5, 0])
        positions['bot_right'] = Vector([c.column + 0.5, c.row - 0.5, 0])
        positions['bot_left'] = Vector([c.column - 0.5, c.row - 0.5, 0])
        positions['top_left_border'] = positions['top_left'] + Vector([1, -1, 0]) * border
        positions['top_right_border'] = positions['top_right'] + Vector([-1, -1, 0]) * border
        positions['bot_right_border'] = positions['bot_right'] + Vector([1, 1, 0]) * border
        positions['bot_left_border'] = positions['bot_left'] + Vector([-1, 1, 0]) * border

        positions[TOP] = c.row + 0.5
        positions[BOT] = c.row - 0.5
        positions[LEFT] = c.column - 0.5
        positions[RIGHT] = c.column + 0.5
        positions[TOP_BORDER] = positions[TOP] - border
        positions[BOT_BORDER] = positions[BOT] + border
        positions[LEFT_BORDER] = positions[LEFT] + border
        positions[RIGHT_BORDER] = positions[RIGHT] - border
        return positions

    def sub_vec(self, vec1, vec2):
        return (vec1[0] - vec2[0], vec1[1] - vec2[1], vec1[2] - vec2[2])

    def get_blueprint(self):
        walls = []
        cells = []
        cells_vertices = []
        for c in self.get_unmasked_and_linked_cells():
            new_walls, new_cells, cell_vertices = self.get_cell_walls(c)
            walls.extend(new_walls)
            cells.extend(new_cells)
            if cell_vertices:
                cells_vertices.append(cell_vertices)
        return walls, cells, cells_vertices

    def need_wall_to(self, c):
        return not c or c.is_masked or not c.has_any_link()

    def get_cell_walls(self, c):
        walls = []
        cells = []
        mask = c.get_wall_mask()
        p = self.get_cell_position(c)
        if mask[0]:
            walls.append(p['top_left'])
            walls.append(p['top_right'])
        if mask[3]:
            walls.append(p['bot_right'])
            walls.append(p['top_right'])
        if self.need_wall_to(c.neighbors[2]):
            walls.append(p['bot_right'])
            walls.append(p['bot_left'])
        if self.need_wall_to(c.neighbors[1]):
            walls.append(p['top_left'])
            walls.append(p['bot_left'])

        cell_corners = 4

        cells.append(Vector([p[RIGHT_BORDER], p[TOP_BORDER], 0]))
        if not mask[0]:
            cells.append(Vector([p[RIGHT_BORDER], p[TOP], 0]))
            cells.append(Vector([p[LEFT_BORDER], p[TOP], 0]))
            cell_corners += 2

        cells.append(Vector([p[LEFT_BORDER], p[TOP_BORDER], 0]))
        if not mask[1]:
            cells.append(Vector([p[LEFT], p[TOP_BORDER], 0]))
            cells.append(Vector([p[LEFT], p[BOT_BORDER], 0]))
            cell_corners += 2

        cells.append(Vector([p[LEFT_BORDER], p[BOT_BORDER], 0]))
        if not mask[2]:
            cells.append(Vector([p[LEFT_BORDER], p[BOT], 0]))
            cells.append(Vector([p[RIGHT_BORDER], p[BOT], 0]))
            cell_corners += 2
        cells.append(Vector([p[RIGHT_BORDER], p[BOT_BORDER], 0]))

        if not mask[3]:
            cells.append(Vector([p[RIGHT], p[BOT_BORDER], 0]))
            cells.append(Vector([p[RIGHT], p[TOP_BORDER], 0]))
            cell_corners += 2

        return walls, cells, cell_corners
