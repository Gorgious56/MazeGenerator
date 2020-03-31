from random import choice, seed, shuffle
from mathutils import Vector
from .. cell import Cell
from .... visual . cell_visual import CellVisual
TOP = 'TOP'
BOT = 'BOT'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
TOP_BORDER = 'TOP_BORDER'
BOT_BORDER = 'BOT_BORDER'
LEFT_BORDER = 'LEFT_BORDER'
RIGHT_BORDER = 'RIGHT_BORDER'
CENTER = 'CENTER'
BORDER = 'BORDER'


class Grid:
    def __init__(self, rows=2, columns=2, levels=1, name="", coord_system='cartesian', sides=4, cell_size=1, space_rep=0):
        self.rows = rows
        self.columns = columns
        self.levels = levels
        self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = []
        self.name = name
        self.space_rep = space_rep

        self.coord_system = coord_system

        self.sides_per_cell = sides

        self.prepare_grid()
        self.configure_cells()

        self.offset = Vector((-self.columns / 2, -self.rows / 2, 0))

        self.cell_size = cell_size

    def __delitem__(self, key):
        del self._cells[key[0] + key[1] * self.columns]

    def __getitem__(self, key):
        key = list(key)
        if len(key) == 2:
            key.append(0)
        if self.space_rep > 0:
            if key[0] == -1:
                key[0] = self.columns - 1
            elif key[0] == self.columns:
                key[0] = 0
            if self.space_rep == 3:
                if key[1] == -1:
                    key[1] = self.rows - 1
                elif key[1] == self.rows:
                    key[1] = 0
        return self._cells[key[0] + key[1] * self.columns + key[2] * self.size_2D] \
            if (self.columns > key[0] >= 0 and self.rows > key[1] >= 0 and self.levels > key[2] >= 0) else None

    def __setitem__(self, key, value):
        if len(key) == 2:
            self.__setitem__((key[0], key[1], 0), value)
        else:
            self._cells[key[0] + key[1] * self.columns + key[2] * self.size_2D] = value

    def prepare_grid(self):
        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = Cell(r, c, l)

    def configure_cells(self):
        for c in self.all_cells():
            row, col, level = c.row, c.column, c.level
            # North :
            c.neighbors[0] = self[col, row + 1, level]
            # West :
            c.neighbors[1] = self[col - 1, row, level]
            # South :
            c.neighbors[2] = self[col, row - 1, level]
            # East :
            c.neighbors[3] = self[col + 1, row, level]
            # Up :
            c.neighbors[4] = self[col, row, level + 1]
            # Up :
            c.neighbors[5] = self[col, row, level - 1]

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            seed(_seed)
        try:
            return choice(self.get_unmasked_cells()) if filter_mask else choice(self.all_cells())
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
        for l in range(self.levels):
            for r in range(self.rows):
                yield [c for c in self._cells[r * cols + l * self.size_2D: (r + 1) * cols + l * self.size_2D] if not c.is_masked]

    def each_level(self):
        for l in range(self.levels):
            yield [c for c in self._cells[l * self.size_2D: (l + 1) * self.size_2D] if not c.is_masked]

    def each_cell(self):
        for c in self.get_unmasked_cells():
            yield c

    def all_cells(self):
        return self._cells

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
                    unconnected_neighbors = [n for n in c.get_neighbors() if n not in c.links and n.has_any_link()]
                    if len(unconnected_neighbors) > 0:
                        best = [n for n in unconnected_neighbors if len(n.links) < 2]
                        if best:
                            dead_ends -= 1
                        else:
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
                    pass
                except AttributeError:
                    pass

    def mask_cell(self, column, row):
        c = self[column, row]
        if c is not None:
            c.is_masked = True
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None
                c.unlink(n)

    def shuffled_cells(self):
        shuffled_cells = self.get_unmasked_cells()
        shuffle(shuffled_cells)
        return shuffled_cells

    def mask_ring(self, center_row, center_col, radius):
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

    def get_unmasked_cells(self):
        return [c for c in self.all_cells() if not c.is_masked]

    def get_unmasked_and_linked_cells(self):
        return [c for c in self.all_cells() if any(c.links)]

    def get_cell_position(self, c, cell_size=None):
        offset = self.offset
        positions = {}
        delta_level = c.level * (self.columns + 1)
        cell_size = self.cell_size if cell_size is None else cell_size
        border = (1 - cell_size) / 2
        positions[TOP] = c.row + 0.5 + offset.y
        positions[BOT] = c.row - 0.5 + offset.y
        positions[LEFT] = c.column - 0.5 + delta_level + offset.x
        positions[RIGHT] = c.column + 0.5 + delta_level + offset.x
        positions[TOP_BORDER] = positions[TOP] - border
        positions[BOT_BORDER] = positions[BOT] + border
        positions[LEFT_BORDER] = positions[LEFT] + border
        positions[RIGHT_BORDER] = positions[RIGHT] - border
        positions[CENTER] = Vector((c.column + delta_level, c.row, 0)) + offset
        positions[BORDER] = cell_size * 0.05
        return positions

    def get_blueprint(self):
        return [self.get_cell_walls(c) for c in self.get_unmasked_and_linked_cells()]

    def need_wall_to(self, c):
        return not c or c.is_masked or not c.has_any_link()

    def get_cell_walls(self, c):
        cv = CellVisual(c)
        p = self.get_cell_position(c)
        mask = c.get_wall_mask()
        left = p[LEFT]
        right = p[RIGHT]
        top = p[TOP]
        bot = p[BOT]
        left_b = p[LEFT_BORDER]
        right_b = p[RIGHT_BORDER]
        bot_b = p[BOT_BORDER]
        top_b = p[TOP_BORDER]
        cx = (right + left) / 2
        cy = (top + bot) / 2
        b = p[BORDER]
        if mask[0]:
            cv.create_wall(Vector((left, top, 0)), Vector((right, top, 0)))
        else:
            cv.add_face(
                (Vector((right_b, top_b, 0)), Vector((right_b, top, 0)), Vector((left_b, top, 0)), Vector((left_b, top_b, 0))),
                vertices_levels=(1, 0, 0, 1))
        if mask[3]:
            cv.create_wall(Vector((right, bot, 0)), Vector((right, top, 0)))
        else:
            cv.add_face(
                (Vector((right_b, bot_b, 0)), Vector((right, bot_b, 0)), Vector((right, top_b, 0)), Vector((right_b, top_b, 0))),
                vertices_levels=(1, 0, 0, 1))
        if self.need_wall_to(c.neighbors[2]):
            cv.create_wall(Vector((right, bot, 0)), Vector((left, bot, 0)))
        if self.need_wall_to(c.neighbors[1]):
            cv.create_wall(Vector((left, top, 0)), Vector((left, bot, 0)))

        cv.add_face(
            (Vector((right_b, top_b, 0)), Vector((left_b, top_b, 0)), Vector((left_b, bot_b, 0)), Vector((right_b, bot_b, 0))),
            vertices_levels=(1, 1, 1, 1))

        if not mask[1]:
            cv.add_face(
                (Vector((left_b, top_b, 0)), Vector((left, top_b, 0)), Vector((left, bot_b, 0)), Vector((left_b, bot_b, 0))),
                vertices_levels=(1, 0, 0, 1))
        if not mask[2]:
            cv.add_face(
                (Vector((left_b, bot_b, 0)), Vector((left_b, bot, 0)), Vector((right_b, bot, 0)), Vector((right_b, bot_b, 0))),
                vertices_levels=(1, 0, 0, 1))

        zd = 0.1
        if not mask[4]:
            cv.add_face(
                (Vector((cx, top_b - b * 1.5, zd)), Vector((cx, bot_b + b * 1.5, zd)), Vector((right_b - b * 1.5, cy, zd))),
                vertices_levels=(1, 1, 1))
        if not mask[5]:
            cv.add_face(
                (Vector((cx, top_b - b * 1.5, zd)), Vector((left_b + b, cy, zd)), Vector((cx, bot_b + b * 1.5, zd))),
                vertices_levels=(1, 1, 1))

        return cv
