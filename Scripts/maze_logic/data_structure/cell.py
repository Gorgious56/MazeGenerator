from random import random, choice, choices


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
        self.links[other_cell] = True
        if bidirectional:
            other_cell.link(self, False)

    def unlink(self, other_cell, bidirectional=True):
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

    def get_neighbors(self):
        return [n for n in self.neighbors if n]

    def get_unlinked_neighbors(self):
        return [c for c in self.get_neighbors() if not c.has_any_link()]

    def get_linked_neighbors(self):
        return [c for c in self.get_neighbors() if c.has_any_link()]

    def exists_and_is_linked(self, other_cell):
        return other_cell is not None and self.is_linked(other_cell)

    def exists_and_is_linked_neighbor_index(self, neighbor_index):
        return self.exists_and_is_linked(self.neighbors[neighbor_index])

    def get_wall_mask(self):
        return [not self.exists_and_is_linked(n) for n in self.neighbors] if self.has_any_link() else [False] * len(self.neighbors)

    def get_biased_choice(self, cell_list, bias, relative_weight=5):
        cell_list_len = len(cell_list)
        try:
            return choices(cell_list, weights=[1 + relative_weight * abs(bias) * (ind if bias >= 0 else cell_list_len - 1 - ind) for ind in range(cell_list_len)])[0]
        except IndexError:
            return None

    def get_biased_unmasked_linked_neighbor(self, bias, relative_weight=5):
        return self.get_biased_choice(self.get_linked_neighbors(), bias, relative_weight)

    def get_biased_unmasked_unlinked_neighbor(self, bias, relative_weight=5):
        return self.get_biased_choice(self.get_unlinked_neighbors(), bias, relative_weight)

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
