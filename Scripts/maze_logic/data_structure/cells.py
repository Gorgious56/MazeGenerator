import random
from Scripts.utils import event
from Scripts.utils import methods
from Scripts.visual import cell_visual
from Scripts.maze_logic.data_structure import constants as cst


class Cell(object):
    """Base class for representing a square cell

    column : Horizontal axis position in the grid
    row: Vertical axis position in the grid
    """
    NEIGHBORS_RETURN = [cst.BCK, cst.RIGHT, cst.FWD, cst.LEFT, cst.DOWN, cst.UP]

    def __init__(self, row, col, level=0):
        self.row = row
        self.column = col
        self.level = level

        self.group = 0

        self._neighbors = [None] * 6

        self.links = {}

        self.visual = cell_visual.CellVisual(self)

    def __str__(self):
        return 'Cell(r' + str(self.row) + ';c' + str(self.column) + ')'

    def __repr__(self):
        return self.__str__()

    def get_neighbor_direction(self, other_cell):
        """Returns this cell's neighbor's direction according to the constants module"""
        try:
            return self._neighbors.index(other_cell)
        except ValueError:
            return -1

    def link(self, other_cell, bidirectional=True):
        if other_cell:
            self.links[other_cell] = True
            if bidirectional:
                other_cell.link(self, False)

    def unlink(self, other_cell, bidirectional=True):
        if other_cell:
            try:
                del self.links[other_cell]
            except KeyError:
                pass
            if bidirectional:
                other_cell.unlink(self, False)

    def is_linked(self, other_cell):
        return other_cell in self.links

    def has_any_link(self):
        return any(self.links)

    def exists_and_is_linked(self, other_cell):
        return other_cell is not None and self.is_linked(other_cell)

    def neighbor_index_exists_and_is_linked(self, neighbor_index):
        return self.exists_and_is_linked(self._neighbors[neighbor_index])

    @property
    def neighbors(self):
        return [n for n in self._neighbors if n]

    def neighbor(self, index):
        return self._neighbors[index] if 0 <= index < len(self._neighbors) else None

    def neighbors_in_range(self, min, max):
        if 0 <= min < max < len(self._neighbors):
            return [n for n in self._neighbors[min: max] if n]
        else:
            return []

    def set_neighbor(self, index, cell):
        try:
            self._neighbors[index] = cell
            if cell:
                cell._neighbors[self.get_neighbor_return(index)] = self
        except IndexError:
            print(f"{self} neighbor n° {index} can't be set")

    def get_unlinked_neighbors(self):
        return [c for c in self.neighbors if not c.has_any_link()]

    def get_linked_neighbors(self):
        return [c for c in self.neighbors if c.has_any_link()]

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self._neighbors] if self.has_any_link() else [False] * len(self._neighbors)

    def get_shuffled_neighbors(self):
        shuffled_neighbors = self.neighbors
        random.shuffle(shuffled_neighbors)
        return shuffled_neighbors

    def get_neighbor_return(self, index):
        return self.NEIGHBORS_RETURN[index]

    def get_biased_neighbors(self, bias, relative_weight=15):
        _neighbors = self.neighbors
        return methods.get_biased_choice(_neighbors, bias, relative_weight, k=len(_neighbors))

    def get_biased_linked_neighbor(self, bias, relative_weight=5):
        return methods.get_biased_choice(self.get_linked_neighbors(), bias, relative_weight)

    def get_neighbor_level_biased(self, bias=0):
        """
        Get a random neighbor
        A bias of 0 will prefer selecting a cell on the same level
        A bias of 1 will prefer selecting a cell on a different level
        """
        pass

    def get_biased_unlinked_directional_neighbor(self, bias, direction):
        direction = int(direction)
        if direction == -1 or type(self) is not Cell:
            try:
                # unlinked_neighbor = self.get_neighbor_level_biased((1 + bias) / 2)
                unlinked_neighbor = random.choice(self.get_unlinked_neighbors())
                return unlinked_neighbor, self.get_neighbor_direction(unlinked_neighbor)
            except IndexError:
                return None, -1
        else:
            left_dir = (direction + 1) % 4
            right_dir = (direction - 1) % 4
            left = self._neighbors[left_dir]
            front = self._neighbors[direction]
            right = self._neighbors[right_dir]

            choose_left = (1 - 2 * bias) / 3
            choose_front = (1 - abs(bias) / 3) / 3

            is_left_available = left and not left.has_any_link()
            is_front_available = front and not front.has_any_link()
            is_right_available = right and not right.has_any_link()
            roll = random.random()

            if choose_left > roll:
                if is_left_available:
                    return left, left_dir
                elif is_front_available:
                    return front, direction
                elif is_right_available:
                    return right, right_dir
            elif choose_left + choose_front > roll:
                if is_front_available:
                    return front, direction
                else:
                    new_roll = random.random()
                    choose_left = (1 - bias) / 2
                    if choose_left > new_roll and is_left_available:
                        return left, left_dir
                    elif is_right_available:
                        return right, right_dir
                    else:
                        return None, -1
            elif is_right_available:
                return right, right_dir
            elif is_front_available:
                return front, direction
            elif is_left_available:
                return left, left_dir
            else:
                return None, -1
            return None, -1


class CellHex(Cell):
    NEIGHBORS_RETURN = [3, 4, 5, 0, 1, 2]

    def __init__(self, row, col, lvl):
        super().__init__(row, col, lvl)
        self._neighbors = [None] * 6


class CellOver(Cell):
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.neighbors_over = None
        self.request_tunnel_under = event.EventHandler(event.Event('Tunnel Under'), self)

    def neighbors(self):
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self.NEIGHBORS_RETURN)
            for i, neighbor in enumerate(self._neighbors):
                self.neighbors_over[i] = neighbor._neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().neighbors
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    def get_neighbors_copy(self):  # Keep this for method patching using Kruskal's algorithm and weave maze until I know how to do it cleanly.
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self.NEIGHBORS_RETURN)
            for i, neighbor in enumerate(self._neighbors):
                self.neighbors_over[i] = neighbor._neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().neighbors
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    def can_tunnel_towards(self, direction):
        potential_host = self._neighbors[direction]
        return potential_host and potential_host._neighbors[direction] and potential_host.can_host_psg_towards(direction)

    def can_host_psg_towards(self, direction):
        return self.can_host_under_vertical_psg() if direction % 2 == 0 else self.can_host_under_horiz_psg()

    def can_host_under_vertical_psg(self):
        return self.is_linked(self._neighbors[1]) and self.is_linked(self._neighbors[3]) and not self.is_linked(self._neighbors[0]) and not self.is_linked(self._neighbors[2])

    def can_host_under_horiz_psg(self):
        return not self.is_linked(self._neighbors[1]) and not self.is_linked(self._neighbors[3]) and self.is_linked(self._neighbors[0]) and self.is_linked(self._neighbors[2])

    def link(self, other_cell, bidirectional=True):
        if other_cell:
            for i, neighbor in enumerate(self._neighbors):
                if neighbor and neighbor == other_cell._neighbors[self.get_neighbor_return(i)]:
                    self.request_tunnel_under(neighbor)
                    return
            else:
                super().link(other_cell, bidirectional=bidirectional)


class CellPolar(Cell):

    def __init__(self, row, col, lvl=0):
        super().__init__(row, col, lvl)
        self.cw = None
        self.ccw = None
        self.inward = None
        self.outward = []

    @property
    def neighbors(self):
        _neighbors = []
        for n in [self.cw, self.ccw, self.inward]:
            if n:
                _neighbors.append(n)
        _neighbors.extend(self.outward)
        return _neighbors

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self._neighbors] if self.has_any_link() else [False] * len(self._neighbors)

    def is_linked_outward(self):
        for n in self.outward:
            if n and self.is_linked(n):
                return True
        return False

    def has_outward_neighbor(self):
        return len(self.outward) > 0


class CellTriangle(Cell):
    NEIGHBORS_RETURN = (0, 1, 2)

    def __init__(self, row, col, lvl):
        super().__init__(row, col, lvl)
        # If Upright : NE, NW, S else : SW, SE, N
        self._neighbors = [None] * 3

    def is_upright(self):
        return (self.row + self.column) % 2 == 1


class CellUnder(Cell):
    def __init__(self, cell_over):
        super().__init__(cell_over.row, cell_over.column)
        _neighbors = (0, 2) if cell_over.can_host_under_vertical_psg() else (1, 3)
        for n in _neighbors:
            try:
                self._neighbors[n] = cell_over._neighbors[n]
                cell_over._neighbors[n]._neighbors[self.get_neighbor_return(n)] = self
                self.link(self._neighbors[n])
            except AttributeError:
                break

    def can_host_under_vertical_psg(self):
        return self._neighbors[1] or self._neighbors[3]

    def can_host_under_horiz_psg(self):
        return self._neighbors[0] or self._neighbors[2]

    def can_host_psg_towards(self, direction):
        return self.can_host_under_horiz_psg() if direction % 2 == 0 else self.can_host_under_vertical_psg()
