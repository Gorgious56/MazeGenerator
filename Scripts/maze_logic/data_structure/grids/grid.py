from random import choice, seed, shuffle
from mathutils import Vector
from .. cell import Cell
from .... visual . space_rep_manager import REP_REGULAR, REP_STAIRS, REP_CYLINDER, REP_MEOBIUS, REP_TORUS, REP_BOX

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

UP, DOWN, LEFT, RIGHT = 0, 2, 1, 3


class Grid:
    def __init__(self, rows=2, columns=2, levels=1, cell_size=1, space_rep=0, mask=None, sides=4):
        self.rows = rows
        self.columns = columns
        self.levels = levels
        self._cells = [None] * (rows * columns * levels)
        self.size = rows * columns * levels
        self.size_2D = rows * columns
        self.masked_cells = []  # This container is used in some algorithms.
        self.space_rep = space_rep

        self.mask = mask

        self.offset = Vector(((1 - self.columns) / 2, (1 - self.rows) / 2, 0))

        self.cell_size = cell_size

        self.number_of_sides = sides

        self.relative_positions_inset = self.get_relative_positions(self.cell_size)
        self.relative_positions_one = self.get_relative_positions(1)
        self.relative_positions_out = self.get_relative_positions_out()

        self.prepare_grid()
        self.configure_cells()

    def __delitem__(self, key):
        del self._cells[key[0] + key[1] * self.columns]

    def __getitem__(self, key):
        key = list(key)
        if len(key) == 2:
            key.append(0)
        if self.space_rep in (int(REP_CYLINDER), int(REP_MEOBIUS), int(REP_TORUS), int):
            if key[0] == -1:
                key[0] = self.columns - 1
            elif key[0] == self.columns:
                key[0] = 0
            if self.space_rep == int(REP_TORUS):
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
        if self.space_rep != int(REP_BOX):
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
                        c.neighbors[UP] = self[rows, 3 * rows - col - 1, level]
                        c.neighbors[UP].neighbors[LEFT] = c
                    elif rows + cols <= col < 2 * rows + cols:
                        c.neighbors[UP] = self[rows + cols - 1, rows - cols + col, level]
                        c.neighbors[UP].neighbors[RIGHT] = c
                    elif col >= 2 * rows + cols:
                        c.neighbors[UP] = self[3 * rows + 2 * cols - 1 - col, 3 * rows - 1, level]
                        c.neighbors[UP].neighbors[UP] = c
                    else:
                        c.neighbors[UP] = self[col, row + 1, level]
                        c.neighbors[UP].neighbors[DOWN] = c
                elif not c.neighbors[UP]:
                    c.neighbors[UP] = self[col, row + 1, level]
                    if c.neighbors[UP]:
                        c.neighbors[UP].neighbors[DOWN] = c
                # West :
                if not c.neighbors[LEFT]:
                    c.neighbors[LEFT] = self[col - 1, row, level]
                    if c.neighbors[LEFT]:
                        c.neighbors[LEFT].neighbors[RIGHT] = c
                # South :
                if row == rows:
                    if col < rows:
                        c.neighbors[DOWN] = self[rows, col, level]
                        c.neighbors[DOWN].neighbors[LEFT] = c
                    elif rows + cols <= col < 2 * rows + cols:
                        c.neighbors[DOWN] = self[rows + cols - 1, 2 * rows + cols - 1 - col, level]
                        c.neighbors[DOWN].neighbors[RIGHT] = c
                    elif col >= 2 * rows + cols:
                        c.neighbors[DOWN] = self[3 * rows + 2 * cols - 1 - col, 0, level]
                        c.neighbors[DOWN].neighbors[DOWN] = c
                    else:
                        c.neighbors[DOWN] = self[col, row - 1, level]
                        c.neighbors[DOWN].neighbors[UP] = c
                # Up :
                if not c.neighbors[4]:
                    c.neighbors[4] = self[col, row, level + 1]
                    if c.neighbors[4]:
                        c.neighbors[5] = c

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

    def get_blueprint(self):
        return [self.set_cell_visuals(c) for c in self.get_linked_cells()]

    def get_cell_center(self, c):
        return Vector((c.column + c.level * (self.columns + 1), c.row, 0)) + self.offset

    def get_relative_positions_out(self):
        cs = self.cell_size
        pos_one, pos_out = self.relative_positions_one, []
        for i in range(self.number_of_sides):
            pos_out.append((pos_one[i] * (1 + cs) + pos_one[(i + 1) % self.number_of_sides] * (1 - cs)) / 2)
            pos_out.append((pos_one[i] * (1 - cs) + pos_one[(i + 1) % self.number_of_sides] * (1 + cs)) / 2)
        return pos_out

    def get_relative_positions(self, size):
        top_right = Vector(((size / 2), (size / 2), 0))
        top_left = Vector(((-size / 2), (size / 2), 0))
        bot_left = Vector(((-size / 2), (-size / 2), 0))
        bot_right = Vector(((size / 2), (-size / 2), 0))
        return top_right, top_left, bot_left, bot_right

    def set_cell_visuals(self, c):
        cv = c.visual
        mask = c.get_wall_mask()
        center = self.get_cell_center(c)
        walls_face = []
        pos_one = [center + vec for vec in self.relative_positions_one]
        if self.cell_size != 1:
            pos_in, pos_out = [center + vec for vec in self.relative_positions_inset], [center + vec for vec in self.relative_positions_out]
        for i in range(self.number_of_sides):
            if mask[i]:
                walls_face.extend((i, (i + 1) % self.number_of_sides))
            elif self.cell_size != 1:
                cv.add_face((pos_in[i], pos_out[2 * i], pos_out[(i * 2) + 1], pos_in[(i + 1) % self.number_of_sides]), walls=(0, 1, 2, 3), vertices_levels=(1, 0, 0, 1))

        cv.add_face(([(pos_one if self.cell_size == 1 else pos_in)[i % self.number_of_sides] for i in range(self.number_of_sides)]), walls=None, vertices_levels=[1] * self.number_of_sides)

        return cv
