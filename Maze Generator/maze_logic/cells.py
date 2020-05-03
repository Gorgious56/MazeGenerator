import random
from ..utils import event
from ..utils import methods
from . import constants as cst


class Cell(object):
    """Base class for representing a square cell

    column : Horizontal axis position in the grid
    row: Vertical axis position in the grid
    """
    _NEIGHBORS_RETURN = [cst.SOUTH, cst.EAST, cst.NORTH, cst.WEST, cst.DOWN, cst.UP]

    def __init__(self, row, col, level=0):
        self.row = row
        self.column = col
        self.level = level

        self.group = 0

        self._neighbors = [None] * 6

        self.links = {}

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

    def get_neighbor_towards(self, direction):
        return self._neighbors[direction] if 0 <= direction < len(self._neighbors) else None

    def get_half_neighbors(self):
        return 0, 1

    def link(self, other_cell, bidirectional=True):
        if other_cell:
            self.links[other_cell] = True
            if bidirectional:
                return other_cell.link(self, False)
            else:
                return self, other_cell

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
        return self.exists_and_is_linked(self.neighbor(neighbor_index))

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

    def get_neighbors_linked_to_me(self):
        return [n for n in self.neighbors if n in self.links]

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self._neighbors] if self.has_any_link() else [False] * len(self._neighbors)

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
    _NEIGHBORS_RETURN = [3, 4, 5, 0, 1, 2]

    def __init__(self, row, col, lvl):
        super().__init__(row, col, lvl)
        self._neighbors = [None] * 6

    def get_half_neighbors(self):
        return 0, 1, 2


class CellPolar(Cell):
    _NEIGHBORS_RETURN = [2, lambda c: c._neighbors[1].get_neighbor_direction(c), 0, 1, 1]

    def __init__(self, row, col, lvl=0):
        super().__init__(row, col, lvl)
        self._neighbors = [None] * 5  # [out_ccw, in_ccw, in_cw, out_cw, out_mid]

    def get_half_neighbors(self):
        return 0, 1

    def get_neighbor_return(self, index):
        ret = self._NEIGHBORS_RETURN[index]
        return ret if type(ret) is int else ret(self)


    def is_linked_outward(self):
        return any([n for n in self._neighbors[3:5] if n and self.is_linked(n)])

    def has_outward_neighbor(self):
        return any(self._neighbors[3:5])

    def add_outward(self, cell):
        if self._neighbors[3]:
            self.set_neighbor(4, cell)
        else:
            self.set_neighbor(3, cell)


class CellTriangle(Cell):
    _NEIGHBORS_RETURN = (0, 1, 2)

    def __init__(self, row, col, lvl):
        super().__init__(row, col, lvl)
        # If Upright : NE, NW, S else : SW, SE, N
        self._neighbors = [None] * 3

    def is_upright(self):
        return (self.row + self.column) % 2 == 0

    def get_half_neighbors(self):
        return (0, 1, 2) if self.is_upright() else []


class CellOver(Cell):
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.neighbors_over = None
        self.request_tunnel_under = event.EventHandler(event.Event('Tunnel Under'), self)
        self.has_cell_under = False

    @property
    def neighbors(self):
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self._NEIGHBORS_RETURN)
            for i, neighbor in enumerate(self._neighbors):
                self.neighbors_over[i] = neighbor._neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().neighbors
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    @property
    def neighbors_copy(self):  # Keep this for method patching using Kruskal's algorithm and weave maze until I know how to do it cleanly.
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self._NEIGHBORS_RETURN)
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
        return self.is_linked_and_cell_over(1) and \
            self.is_linked_and_cell_over(3) and not \
            self.is_linked_and_cell_over(0) and not \
            self.is_linked_and_cell_over(2)

    def can_host_under_horiz_psg(self):
        return not self.is_linked_and_cell_over(1) and \
            not self.is_linked_and_cell_over(3) and \
            self.is_linked_and_cell_over(0) and \
            self.is_linked_and_cell_over(2)

    def is_linked_and_cell_over(self, index):
        """
        Check if the cell is not between two Under Cells

        params :
        index : Neighbor Index
        """
        neighbor = self.neighbor(index)
        return type(neighbor) is not CellUnder and self.is_linked(neighbor)

    def link(self, other_cell, bidirectional=True):
        if other_cell:
            for i, neighbor in enumerate(self._neighbors):
                if neighbor and neighbor == other_cell.neighbor(self.get_neighbor_return(i)):
                    return self, self.request_tunnel_under(neighbor)
            else:
                return super().link(other_cell, bidirectional=bidirectional)


class CellUnder(Cell):
    def __init__(self, cell_over):
        super().__init__(cell_over.row, cell_over.column)
        neigh_idx = (cst.NORTH, cst.SOUTH) if cell_over.can_host_under_vertical_psg() else (cst.WEST, cst.EAST)
        for n_idx in neigh_idx:
            self.set_neighbor(n_idx, cell_over.neighbor(n_idx))
            cell_over.set_neighbor(n_idx, None)
            self.link(self.neighbor(n_idx))
        cell_over.has_cell_under = True

    def can_host_under_vertical_psg(self):
        return (self.neighbor(cst.WEST) and type(self.neighbor(cst.WEST)) is not CellUnder) \
            or (self.neighbor(cst.EAST) and type(self.neighbor(cst.EAST)) is not CellUnder)

    def can_host_under_horiz_psg(self):
        return (self.neighbor(cst.NORTH) and type(self.neighbor(cst.NORTH)) is not CellUnder) \
            or (self.neighbor(cst.SOUTH) and type(self.neighbor(cst.SOUTH)) is not CellUnder)

    def can_host_psg_towards(self, direction):
        return self.can_host_under_horiz_psg() if direction % 2 == 0 else self.can_host_under_vertical_psg()
