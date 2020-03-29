from random import random, choice, choices, shuffle
from ... utils . event import Event, EventHandler


class Cell:
    neighbors_return = [2, 3, 0, 1]

    def __init__(self, row, col):
        self.row = row
        self.column = col

        self.group = 0

        self.neighbors = [None] * 4
        # 0>North - 1>West - 2>South - 3>East

        self.links = {}

        self.is_masked = False

    def __str__(self):
        return 'Cell(r' + str(self.row) + ';c' + str(self.column) + ')'

    def __repr__(self):
        return self.__str__()

    def get_direction(self, other_cell):
        try:
            return self.neighbors.index(other_cell)
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

    def exists_and_is_linked_neighbor_index(self, neighbor_index):
        return self.exists_and_is_linked(self.neighbors[neighbor_index])

    def get_neighbors(self):
        return [n for n in self.neighbors if n]

    def get_unlinked_neighbors(self):
        return [c for c in self.get_neighbors() if not c.has_any_link()]

    def get_linked_neighbors(self):
        return [c for c in self.get_neighbors() if c.has_any_link()]

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self.neighbors] if self.has_any_link() else [False] * len(self.neighbors)

    def get_biased_choice(self, cell_list, bias, relative_weight=5, k=1):
        cell_list_len = len(cell_list)
        try:
            if bias == 0:
                shuffle(cell_list)
                return cell_list[0: k + 1] if k > 1 else cell_list[0]
            ret = choices(cell_list, weights=[1 + relative_weight * abs(bias) * (ind if bias >= 0 else cell_list_len - 1 - ind) for ind in range(cell_list_len)], k=k)
            return ret[0] if k == 1 else ret
        except IndexError:
            return None

    def get_shuffled_neighbors(self):
        shuffled_neighbors = self.get_neighbors()
        shuffle(shuffled_neighbors)
        return shuffled_neighbors

    def get_neighbor_return(self, index):
        return self.neighbors_return[index]

    def get_biased_unmasked_neighbors(self, bias, relative_weight=15):
        neighbors = self.get_neighbors()
        return self.get_biased_choice(neighbors, bias, relative_weight, k=len(neighbors))

    def get_biased_unmasked_linked_neighbor(self, bias, relative_weight=5):
        return self.get_biased_choice(self.get_linked_neighbors(), bias, relative_weight)

    def get_biased_unmasked_unlinked_neighbor(self, bias, relative_weight=5):
        return self.get_biased_choice(self.get_unlinked_neighbors(), bias, relative_weight)

    def get_biased_unmasked_unlinked_neighbors(self, bias, relative_weight=5):
        neighbors = self.get_unlinked_neighbors()
        return self.get_biased_choice(neighbors, bias, relative_weight, k=len(neighbors))

    def get_biased_unmasked_unlinked_directional_neighbor(self, bias, direction):
        direction = int(direction)
        if direction == -1 or type(self) is not Cell:
            try:
                unlinked_neighbor = choice(self.get_unlinked_neighbors())
                return unlinked_neighbor, self.get_direction(unlinked_neighbor)
            except IndexError:
                return None, -1
        else:
            left_dir = (direction + 1) % 4
            right_dir = (direction - 1) % 4
            left = self.neighbors[left_dir]
            front = self.neighbors[direction]
            right = self.neighbors[right_dir]

            choose_left = (1 - 2 * bias) / 3
            choose_front = (1 - abs(bias) / 3) / 3

            is_left_available = left and not left.has_any_link()
            is_front_available = front and not front.has_any_link()
            is_right_available = right and not right.has_any_link()
            roll = random()

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
                    new_roll = random()
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
    neighbors_return = [3, 4, 5, 0, 1, 2]

    def __init__(self, row, col):
        super().__init__(row, col)
        self.neighbors = [None] * 6


class CellOver(Cell):
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.neighbors_over = None
        self.request_tunnel_under = EventHandler(Event('Tunnel Under'), self)

    def get_neighbors(self):
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self.neighbors_return)
            for i, neighbor in enumerate(self.neighbors):
                self.neighbors_over[i] = neighbor.neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().get_neighbors()
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    def get_neighbors_copy(self):  # Keep this for method patching using Kruskal's algorithm and weave maze until I know how to do it cleanly.
        if self.neighbors_over is None:
            self.neighbors_over = [None] * len(self.neighbors_return)
            for i, neighbor in enumerate(self.neighbors):
                self.neighbors_over[i] = neighbor.neighbors[i] if self.can_tunnel_towards(i) else None
        ns = super().get_neighbors()
        ns.extend([n for n in self.neighbors_over if n])
        return ns

    def can_tunnel_towards(self, direction):
        potential_host = self.neighbors[direction]
        return potential_host and potential_host.neighbors[direction] and potential_host.can_host_psg_towards(direction)

    def can_host_psg_towards(self, direction):
        return self.can_host_under_vertical_psg() if direction % 2 == 0 else self.can_host_under_horiz_psg()

    def can_host_under_vertical_psg(self):
        return self.is_linked(self.neighbors[1]) and self.is_linked(self.neighbors[3]) and not self.is_linked(self.neighbors[0]) and not self.is_linked(self.neighbors[2])

    def can_host_under_horiz_psg(self):
        return not self.is_linked(self.neighbors[1]) and not self.is_linked(self.neighbors[3]) and self.is_linked(self.neighbors[0]) and self.is_linked(self.neighbors[2])

    def link(self, other_cell, bidirectional=True):
        if other_cell:
            for i, neighbor in enumerate(self.neighbors):
                if neighbor and neighbor == other_cell.neighbors[self.get_neighbor_return(i)]:
                    self.request_tunnel_under(neighbor)
                    return
            else:
                super().link(other_cell, bidirectional=bidirectional)


class CellPolar(Cell):

    def __init__(self, row, column):
        super().__init__(row, column)
        self.cw = None
        self.ccw = None
        self.inward = None
        self.outward = []

    def get_neighbors(self):
        neighbors = []
        for n in [self.cw, self.ccw, self.inward]:
            if n:
                neighbors.append(n)
        neighbors.extend(self.outward)
        return neighbors

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self.neighbors] if self.has_any_link() else [False] * len(self.neighbors)

    def is_linked_outward(self):
        for n in self.outward:
            if n and self.is_linked(n):
                return True
        return False

    def has_outward_neighbor(self):
        return len(self.outward) > 0


class CellTriangle(Cell):
    neighbors_return = [0, 2, 1]

    def __init__(self, row, col):
        super().__init__(row, col)
        # If Upright : NE, NW, S else : SW, SE, N
        self.neighbors = [None] * 3

    def is_upright(self):
        return (self.row + self.column) % 2 == 1


class CellUnder(Cell):
    def __init__(self, cell_over):
        super().__init__(cell_over.row, cell_over.column)
        neighbors = (0, 2) if cell_over.can_host_under_vertical_psg() else (1, 3)
        for n in neighbors:
            try:
                self.neighbors[n] = cell_over.neighbors[n]
                cell_over.neighbors[n].neighbors[self.get_neighbor_return(n)] = self
                self.link(self.neighbors[n])
            except AttributeError:
                break

    def can_host_under_vertical_psg(self):
        return self.neighbors[1] or self.neighbors[3]

    def can_host_under_horiz_psg(self):
        return self.neighbors[0] or self.neighbors[2]

    def can_host_psg_towards(self, direction):
        return self.can_host_under_horiz_psg() if direction % 2 == 0 else self.can_host_under_vertical_psg()