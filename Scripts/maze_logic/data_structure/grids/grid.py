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
    def __init__(self, rows=2, columns=2, levels=1, cell_size=1, space_rep=0, mask=None):
        self.rows = rows
        self.columns = columns
        self.levels = levels
        self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = []  # This container is used in some algorithms.
        self.space_rep = space_rep

        self.mask = mask

        self.offset = Vector((-self.columns / 2, -self.rows / 2, 0))

        self.cell_size = cell_size

        self.prepare_grid()
        self.configure_cells()

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
        if self.mask:
            [self.mask_patch(mask_patch[0], mask_patch[1], mask_patch[2], mask_patch[3],) for mask_patch in self.mask]

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    self[c, r, l] = Cell(r, c, l) if self[c, r, l] is None else None

    def set_neighbor_return(self, cell_a, cell_b, number):
        cell_a.neighbors[number] = cell_b
        if cell_b:
            cell_b.neighbors[cell_b.get_neighbor_return(number)] = cell_a

    def configure_cells(self):
        # 0>North - 1>West - 2>South - 3>East - 4>Up - 5>Down
        if self.space_rep != 4:
            for c in self.all_cells():
                row, col, level = c.row, c.column, c.level
                self.set_neighbor_return(c, self[col, row + 1, level], 0)
                self.set_neighbor_return(c, self[col - 1, row, level], 1)
                self.set_neighbor_return(c, self[col, row, level + 1], 4)
        else:
            rows = int(self.rows / 3)
            cols = int(self.columns / 2 - rows)
            for c in self.all_cells():
                row, col, level = c.row, c.column, c.level
                # North :
                if row == 2 * rows - 1:
                    if col < rows:
                        c.neighbors[0] = self[rows, 3 * rows - col - 1, level]
                        c.neighbors[0].neighbors[1] = c
                    elif rows + cols <= col < 2 * rows + cols:
                        c.neighbors[0] = self[rows + cols - 1, rows - cols + col, level]
                        c.neighbors[0].neighbors[3] = c
                    elif col >= 2 * rows + cols:
                        c.neighbors[0] = self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level]
                        c.neighbors[0].neighbors[0] = c
                    else:
                        c.neighbors[0] = self[col, row + 1, level]
                        c.neighbors[0].neighbors[2] = c
                elif not c.neighbors[0]:
                    c.neighbors[0] = self[col, row + 1, level]
                    c.neighbors[0].neighbors[2] = c
                # West :
                if not c.neighbors[1]:
                    c.neighbors[1] = self[col - 1, row, level]
                # South :
                if row == rows:
                    if col < rows:
                        c.neighbors[2] = self[rows, col, level]
                        c.neighbors[2].neighbors[1] = c
                    elif rows + cols <= col < 2 * rows + cols:
                        c.neighbors[2] = self[rows + cols - 1, 2 * rows + cols - 1 - col, level]
                        c.neighbors[2].neighbors[3] = c
                    elif col >= 2 * rows + cols:
                        c.neighbors[2] = self[3 * rows + 2 * cols - 1 - col, 0, level]
                        c.neighbors[2].neighbors[2] = c
                    else:
                        c.neighbors[2] = self[col, row - 1, level]
                        c.neighbors[2].neighbors[0] = c
                # East :
                if not c.neighbors[3]:
                    c.neighbors[3] = self[col + 1, row, level]
                # Up :
                if not c.neighbors[4]:
                    c.neighbors[4] = self[col, row, level + 1]
                    c.neighbors[5] = c
                # Up :
                # if not c.neighbors[5]:
                #     c.neighbors[5] = self[col, row, level - 1]

    def mask_patch(self, first_cell_x, first_cell_y, last_cell_x, last_cell_y):
        for c in range(first_cell_x, last_cell_x + 1):
            for r in range(first_cell_y, last_cell_y + 1):
                self[c, r] = 0

    def get_linked_cells(self):
        return [c for c in self.all_cells() if any(c.links)]

    def mask_cell(self, column, row):
        c = self[column, row]
        if c is not None:
            self.masked_cells.append(c)
            for i, n in enumerate(c.get_neighbors()):
                n.neighbors[c.neighbors_return[i]] = None
                c.unlink(n)

    def random_cell(self, _seed=None, filter_mask=True):
        if _seed:
            seed(_seed)
        try:
            return choice(self.all_cells()) if filter_mask else choice(self.all_cells())
        except IndexError:
            return None

    def get_random_linked_cell(self, _seed=None):
        if _seed:
            seed(_seed)
        try:
            return choice(self.get_linked_cells())
        except IndexError:
            return None

    def each_row(self):
        cols = self.columns
        for l in range(self.levels):
            for r in range(self.rows):
                yield [c for c in self._cells[r * cols + l * self.size_2D: (r + 1) * cols + l * self.size_2D] if c]

    def each_level(self):
        for l in range(self.levels):
            yield [c for c in self._cells[l * self.size_2D: (l + 1) * self.size_2D]]

    def each_cell(self):
        for c in self.all_cells():
            yield c

    def all_cells(self):
        return [c for c in self._cells if c]

    def get_dead_ends(self):
        return [c for c in self.all_cells() if len(c.links) == 1]

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
        max_cells_to_cull = len(self.get_linked_cells()) * (sparse / 100) - 2
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

    def shuffled_cells(self):
        shuffled_cells = self.all_cells()
        shuffle(shuffled_cells)
        return shuffled_cells

    def mask_ring(self, center_row, center_col, radius):
        for r in range(self.rows):
            for c in range(self.columns):
                if ((center_col - c) ** 2 + (center_row - r) ** 2) ** 0.5 > radius:
                    self.mask_cell(c, r)

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
        return [self.get_cell_walls(c) for c in self.get_linked_cells()]

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
        if mask[2]:
            cv.create_wall(Vector((right, bot, 0)), Vector((left, bot, 0)))
        if mask[1]:
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
