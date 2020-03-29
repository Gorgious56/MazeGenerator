from random import seed, choice, choices, random, randint, shuffle
from math import ceil
from . data_structure . cell import CellPolar, CellTriangle, CellHex
from .. utils . priority_queue import PriorityQueue
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, SQUARE
from .. utils . union_find import UnionFind


def work(algorithm, grid, seed, max_steps=-1, bias=0):
    try:
        ALGORITHM_FROM_NAME[algorithm](grid, seed, max_steps, bias)
    except KeyError:
        pass


class MazeAlgorithm(object):
    biased = True
    weaved = True

    def __init__(self, grid=None, _seed=None, _max_steps=0, bias=0):
        self.grid = grid
        self.bias = bias
        self._seed = _seed
        seed(self._seed)
        self.__max_steps = 100000 if _max_steps <= 0 else _max_steps
        self.__steps = 0

    def is_last_step(self):
        self.__steps += 1
        return self.__steps >= self.__max_steps

    def add_template_passages(self):
        grid = self.grid
        if hasattr(grid, 'weave'):
            potential_passages = []
            for c in range(1, grid.columns - 1):
                for r in range(1, grid.rows - 1):
                    potential_passages.append(grid[c, r])
            shuffle(potential_passages)

            for pp in potential_passages[0: round(grid.weave * len(potential_passages))]:
                self.add_crossing(pp)

    def color_cells_by_tree_root(self, union_find):
        links = []
        for c in self.grid.all_cells():
            link = union_find.find(c)
            if link:
                try:
                    c.group = links.index(link)
                except ValueError:
                    links.append(link)
                    c.group = len(links) - 1

    def add_crossing(self, cell):
        can_cross = not cell.has_any_link()
        if can_cross:
            north = cell.neighbors[0]
            west = cell.neighbors[1]
            south = cell.neighbors[2]
            east = cell.neighbors[3]
            if random() > 0.5:  # Vertical underway
                pass
                cell.link(west)
                self.union_find.union(cell, east)
                cell.link(east)
                self.union_find.union(cell, east)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                north.link(north.neighbors[cell.neighbors_return[0]])
                self.union_find.union(north, north.neighbors[cell.neighbors_return[0]])
                south.link(south.neighbors[cell.neighbors_return[2]])
                self.union_find.union(south, south.neighbors[cell.neighbors_return[2]])
            else:
                cell.link(north)
                self.union_find.union(cell, north)
                cell.link(south)
                self.union_find.union(cell, south)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                west.link(west.neighbors[cell.neighbors_return[1]])
                self.union_find.union(west, west.neighbors[cell.neighbors_return[1]])
                east.link(east.neighbors[cell.neighbors_return[3]])
                self.union_find.union(east, east.neighbors[cell.neighbors_return[3]])


class BinaryTree(MazeAlgorithm):
    name = 'Binary Tree'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run()
        # self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        bias = self.bias
        for c in grid.each_cell():
            c_type = type(c)
            if c_type is CellTriangle:
                if c.is_upright():
                    neighbors = [c.neighbors[0]] if c.row == grid.rows - 1 and c.neighbors[0] else [n for n in c.neighbors[0:2] if n]
                else:
                    neighbors = [c.neighbors[1]] if c.row == grid.rows - 1 and c.neighbors[1] else [n for n in [c.neighbors[2]] if n]
            elif c_type is CellHex:
                neighbors = [n for n in [c.neighbors[5 if c.column % 2 == 0 else 0]] if n] if c.row == grid.rows - 1 else [n for n in c.neighbors[0:3] if n]
            elif c_type is CellPolar:
                neighbors = c.outward
                if c.ccw and c.column != len(grid.rows_polar[c.row]) - 1:
                    neighbors.append(c.ccw)
            else:  # Square Cell
                neighbors = [n for n in c.neighbors[0:2] if n]

            c.link(c.get_biased_choice(neighbors, bias, 5))

            if self.is_last_step():
                return


class Sidewinder(MazeAlgorithm):
    name = 'Sidewinder'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        # self.union_find = UnionFind(self.grid.all_cells())

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        for row in grid.each_row():
            run = []
            for c in row:
                run.append(c)

                c_type = type(c)
                if c_type is CellTriangle:
                    if c.is_upright():
                        if c.neighbors[0]:
                            c.link(c.neighbors[0])
                        else:
                            if len(run) == 1:
                                c.link(c.neighbors[1])
                            else:
                                member = choice([c for c in run if not c.is_upright()])
                                if member.neighbors[2]:
                                    member.link(member.neighbors[2])
                            run = []
                        if c.row == grid.rows - 1 and c.neighbors[1]:
                            c.link(c.neighbors[1])
                    else:
                        if (c.neighbors[1] is None) or (c.neighbors[1] is not None and self.must_close_run()):
                            member = choice([c for c in run if not c.is_upright()])
                            if member.neighbors[2]:
                                member.link(member.neighbors[2])
                            run = []
                        else:
                            c.link(c.neighbors[1])
                elif c_type is CellHex:
                    other = 5 if c.column % 2 == 0 else 0
                    if (c.neighbors[other] is None) or (c.neighbors[other] and self.must_close_run()):
                        member = choice(run)
                        north_neighbors = [n for n in c.neighbors[0:3] if n and not n.has_any_link()]
                        if north_neighbors:
                            member.link(choice(north_neighbors))
                        elif c.neighbors[5]:
                            c.link(c.neighbors[other])
                        run = []
                    else:
                        c.link(c.neighbors[other])
                elif c_type is CellPolar:
                    if (c.ccw and c.ccw.column == 0) or (c.has_outward_neighbor() and self.must_close_run()) or (c.row == 0):
                        member = choice(run)
                        if member.has_outward_neighbor():
                            member.link(choice(member.outward))
                        run = []
                    else:
                        c.link(c.ccw)
                else:
                    if (c.neighbors[3] is None) or (c.neighbors[0] and self.must_close_run()):
                        member = choice(run)
                        if member.neighbors[0]:
                            member.link(member.neighbors[0])
                        run = []
                    else:
                        c.link(c.neighbors[3])

                if self.is_last_step():
                    return

    def must_close_run(self):
        return self.bias > random()


class Eller(MazeAlgorithm):
    name = 'Eller'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells())

        self.run()

        self.color_cells_by_tree_root(self.union_find)

    def run(self):
        uf = self.union_find
        grid = self.grid
        for row in grid.each_row():
            sets_this_row = {}
            for c in row:
                if c.neighbors[3] and (c.row == grid.rows - 1 or (self.bias < random() and not uf.connected(c, c.neighbors[3]))):
                    c.link(c.neighbors[3])
                    uf.union(c, c.neighbors[3])
                    if self.is_last_step():
                        return
            for c in row:
                this_set = uf.find(c)
                try:
                    sets_this_row[this_set].append(c)
                except KeyError:
                    sets_this_row[this_set] = [c]
            if c.row != grid.rows - 1:
                for tree, cells in sets_this_row.items():
                    b = ceil(self.bias * len(cells))
                    rd= randint(1, b + 1)
                    ch_len = min(len(cells), rd)
                    for c in choices(cells, k=ch_len):
                        if c.neighbors[0]:
                            c.link(c.neighbors[0])
                            uf.union(c, c.neighbors[0])
                            if self.is_last_step():
                                return


class CrossStitch(MazeAlgorithm):
    name = 'Cross-Stitch'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expeditions = 1
        self.unvisited_legit_cells = []
        self.current = None

        self.run()

    def run(self):
        grid = self.grid
        _seed = self._seed
        direction = -1
        self.set_current(grid.random_cell(_seed))

        self.current.group = 1

        while self.current:
            unvisited_neighbor, direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(self.bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
                if self.is_last_step():
                    return
            else:
                self.set_current(None)

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if not c.has_any_link():
                    neighbor = c.get_biased_unmasked_linked_neighbor(self.bias, 5)
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)
                        if self.is_last_step():
                            return

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        try:
            self.unvisited_legit_cells.remove(c)
        except ValueError:
            pass
        other_c.group = self.expeditions + 2

    def set_current(self, c):
        self.current = c
        if c:
            c.group = self.expeditions
            unvisited_neighbors = self.current.get_unlinked_neighbors()
            self.add_to_unvisited_legit_cells(unvisited_neighbors)
        else:
            self.direction = - 1

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])


class KruskalRandom(MazeAlgorithm):
    name = 'Kruskal Randomized'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.union_find = UnionFind(self.grid.all_cells())

        self.add_template_passages()

        self.run()
        self.color_cells_by_tree_root(self.union_find)

    def run(self):
        grid = self.grid
        unvisited_cells = grid.shuffled_cells()
        for c in unvisited_cells:
            for n in c.get_biased_unmasked_neighbors(self.bias):
                if not self.union_find.connected(c, n):
                    c.link(n)
                    self.union_find.union(c, n)
                    if self.is_last_step():
                        return


class Prim(MazeAlgorithm):
    name = 'Prim'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bias = round((1 - abs(self.bias)) * 10)

        self.union_find = UnionFind(self.grid.all_cells())

        self.q = PriorityQueue()
        self.run()
        self.color_cells_by_tree_root(self.union_find)

    def run(self):
        start_cell = self.grid.random_cell()
        self.push_to_queue(start_cell)

        while not self.q.is_empty():
            cell, neighbor = self.q.pop()
            if not self.union_find.connected(cell, neighbor):
                cell.link(neighbor)
                self.union_find.union(cell, neighbor)
                if self.is_last_step():
                    return
                self.push_to_queue(neighbor)
            self.push_to_queue(cell)

    def push_neighbors_to_queue(self, cell):
        [self.push_to_queue(n) for n in cell.get_unlinked_neighbors()]

    def push_to_queue(self, cell, priority=None):
        try:
            self.q.push((cell, choice(cell.get_unlinked_neighbors())), priority if priority else (randint(0, self.bias)))
        except IndexError:
            pass


class GrowingTree(MazeAlgorithm):
    name = 'Growing Tree'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weights = 0.5 - self.bias / 2, 0.5 + self.bias / 2

        self.run()

    def run(self):
        active_cells = [self.grid.random_cell()]

        while active_cells:
            cell = choices((self.last_element_in_list, choice), weights=self.weights)[0](active_cells)
            try:
                available_neighbor = choice(cell.get_unlinked_neighbors())
                cell.link(available_neighbor)
                active_cells.append(available_neighbor)
            except IndexError:
                active_cells.remove(cell)

    def last_element_in_list(self, l):
        return l[-1] if l else None


class AldousBroder(MazeAlgorithm):
    name = 'Aldous-Broder'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        expeditions = 1
        current = grid.random_cell(self._seed, True)
        current.group = expeditions

        unvisited = grid.size - 1 - len(grid.masked_cells)
        while unvisited > 0:

            neighbor = choice(current.get_neighbors())

            if len(neighbor.links) <= 0:
                current.link(neighbor)
                unvisited -= 1
                if self.is_last_step():
                    return
            current = neighbor
            current.group = expeditions


class Wilson(MazeAlgorithm):
    name = 'Wilson'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        unvisited = grid.get_unmasked_cells().copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0:
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited:
                cell = choice([c for c in cell.get_neighbors() if c != path[-1]])
                try:
                    path = path[0:path.index(cell) + 1]
                except ValueError:
                    path.append(cell)

            for i in range(0, len(path) - 1):
                path[i].link(path[i + 1])
                path[i].group = 1
                path[i + 1].group = 1
                unvisited.remove(path[i])
                if self.is_last_step():
                    return


class HuntAndKill(MazeAlgorithm):
    name = 'Hunt And Kill'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unvisited_legit_cells = []
        self.expeditions = 2
        self.direction = - 1

        self.run()

    def run(self):
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

        while self.current:
            while self.current:
                neighbor, self.direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(self.bias, self.direction)
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                    if self.is_last_step():
                        return
                else:
                    self.current = None
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)
                if self.is_last_step():
                    return

                self.direction = neighbor.get_direction(self.current)

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def link_to(self, c, other_c):
        c.link(other_c)
        try:
            self.unvisited_legit_cells.remove(other_c)
        except ValueError:
            pass
        try:
            self.unvisited_legit_cells.remove(c)
        except ValueError:
            pass
        other_c.group = self.expeditions

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions
        unvisited_neighbors = self.current.get_unlinked_neighbors()
        self.add_to_unvisited_legit_cells(unvisited_neighbors)

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])


class RecursiveBacktracker(MazeAlgorithm):
    name = 'Recursive Backtracker'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        expeditions = 1

        stack = [self.grid.random_cell(self._seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        direction = - 1

        while len(stack) > 0:
            current = stack[-1]

            unlinked_neighbor, direction = current.get_biased_unmasked_unlinked_directional_neighbor(self.bias, direction)
            if unlinked_neighbor:
                current.link(unlinked_neighbor)
                if self.is_last_step():
                    return
                stack.append(unlinked_neighbor)
                unlinked_neighbor.group = expeditions + 1
                backtracking = False
            else:
                stack.pop()
                if backtracking:
                    current.group = - 1
                else:
                    expeditions += 1
                backtracking = True


ALGORITHMS = MazeAlgorithm.__subclasses__()
ALGORITHMS_NAMES = [alg_class.name for alg_class in ALGORITHMS]
ALGORITHM_FROM_NAME = {}
[ALGORITHM_FROM_NAME.update({alg_class.name: alg_class}) for alg_class in ALGORITHMS]
DEFAULT_ALGO = RecursiveBacktracker.name

BIASED_ALGORITHMS = [algo.name for algo in ALGORITHMS if algo.biased]
WEAVED_ALGORITHMS = [algo.name for algo in ALGORITHMS if algo.weaved]


def is_algo_biased(props):
    return props.cell_type == SQUARE and props.maze_algorithm in BIASED_ALGORITHMS


def is_algo_weaved(props):
    return props.cell_type == SQUARE and props.maze_algorithm in WEAVED_ALGORITHMS


def generate_algo_enum():
    print([(alg_name, alg_name, '') for alg_name in ALGORITHMS_NAMES])
    return [(alg_name, alg_name, '') for alg_name in ALGORITHMS_NAMES]
