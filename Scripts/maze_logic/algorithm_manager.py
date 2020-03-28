from random import seed, choice, choices, random, shuffle
from . data_structure . cell import CellPolar, CellTriangle, CellHex
from .. visual . cell_type_manager import POLAR, TRIANGLE, HEXAGON, SQUARE


DEFAULT_ALGO = 'ALGO_RECURSIVE_BACKTRACKER'

ALGO_BINARY_TREE = 'ALGO_BINARY_TREE'
ALGO_SIDEWINDER = 'ALGO_SIDEWINDER'
ALGO_CROSS_STITCH = 'ALGO_CROSS_STITCH'
ALGO_ALDOUS_BRODER = 'ALGO_ALDOUS_BRODER'
ALGO_WILSON = 'ALGO_WILSON'
ALGO_HUNT_AND_KILL = 'ALGO_HUNT_AND_KILL'
ALGO_RECURSIVE_BACKTRACKER = 'ALGO_RECURSIVE_BACKTRACKER'
ALGO_ELLER = 'ALGO_ELLER'
ALGO_KRUSKAL_RANDOM = 'ALGO_KRUSKAL_RANDOM'

BIASED_ALGORITHMS = ALGO_RECURSIVE_BACKTRACKER, ALGO_HUNT_AND_KILL, ALGO_SIDEWINDER, ALGO_BINARY_TREE, ALGO_CROSS_STITCH, ALGO_ELLER, ALGO_KRUSKAL_RANDOM
WEAVED_ALGORITHMS = ALGO_RECURSIVE_BACKTRACKER, ALGO_HUNT_AND_KILL, ALGO_WILSON, ALGO_ALDOUS_BRODER, ALGO_KRUSKAL_RANDOM, ALGO_CROSS_STITCH


def is_algo_biased(props):
    return \
        props.maze_algorithm in BIASED_ALGORITHMS \
        and not (props.maze_algorithm in (ALGO_RECURSIVE_BACKTRACKER, ALGO_HUNT_AND_KILL) and props.cell_type in (TRIANGLE, POLAR, HEXAGON))


def is_algo_weaved(props):
    return props.cell_type == SQUARE and props.maze_algorithm in WEAVED_ALGORITHMS


def generate_algo_enum():
    return [(ALGO_BINARY_TREE, 'Binary Tree', ''),
            (ALGO_SIDEWINDER, 'Sidewinder', ''),
            (ALGO_ELLER, 'Eller', ''),
            (ALGO_CROSS_STITCH, 'Cross Stitch', ''),
            (ALGO_KRUSKAL_RANDOM, 'Kruskal Randomized', ''),
            (ALGO_ALDOUS_BRODER, 'Aldous-Broder', ''),
            (ALGO_WILSON, 'Wilson', ''),
            (ALGO_HUNT_AND_KILL, 'Hunt And Kill', ''),
            (ALGO_RECURSIVE_BACKTRACKER, 'Recursive Backtracker', ''),
            ]


def work(algorithm, grid, seed, max_steps=-1, bias=0):
    algo = None
    if algorithm == ALGO_BINARY_TREE:
        algo = BinaryTree
    elif algorithm == ALGO_SIDEWINDER:
        algo = Sidewinder
    elif algorithm == ALGO_CROSS_STITCH:
        algo = CrossStitch
    elif algorithm == ALGO_ALDOUS_BRODER:
        algo = AldousBroder
    elif algorithm == ALGO_WILSON:
        algo = Wilson
    elif algorithm == ALGO_HUNT_AND_KILL:
        algo = HuntAndKill
    elif algorithm == ALGO_RECURSIVE_BACKTRACKER:
        algo = RecursiveBacktracker
    elif algorithm == ALGO_ELLER:
        algo = Eller
    elif algorithm == ALGO_KRUSKAL_RANDOM:
        algo = KruskalRandom
    if algo:
        algo(grid, seed, max_steps, bias)


class MazeAlgorithm:
    def __init__(self, _seed=None, _max_steps=0, bias=0):
        self.bias = bias
        self._seed = _seed
        seed(self._seed)
        self.__max_steps = 100000 if _max_steps <= 0 else _max_steps
        self.__steps = 0

    def must_break(self):
        return self.__steps >= self.__max_steps

    def next_step(self):
        self.__steps += 1

    def color_cells_by_tree_root(self, cells):
        trees = []
        for c in cells:
            try:
                this_root = c.get_root()
                c.group = trees.index(this_root)
            except ValueError:
                trees.append(this_root)
                c.group = len(trees) - 1


class BinaryTree(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        for c in grid.each_cell():
            if self.must_break():
                break
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

            self.next_step()

        self.color_cells_by_tree_root(grid.each_cell())


class AldousBroder(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        expeditions = 1
        current = grid.random_cell(_seed, True)
        current.group = expeditions

        unvisited = grid.size - 1 - len(grid.masked_cells)
        while unvisited > 0 and not self.must_break():

            neighbor = choice(current.get_neighbors())

            if len(neighbor.links) <= 0:
                current.link(neighbor)
                unvisited -= 1
                self.next_step()
            current = neighbor
            current.group = expeditions


class CrossStitch(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        self.expeditions = 1

        self.unvisited_legit_cells = []

        direction = -1
        self.current = None

        self.set_current(grid.random_cell(_seed))

        self.current.group = 1

        while self.current and not self.must_break():
            unvisited_neighbor, direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
            else:
                self.set_current(None)
            self.next_step()

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if self.must_break():
                    break
                if not c.has_any_link():
                    neighbor = c.get_biased_unmasked_linked_neighbor(bias, 5)
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)
                        self.next_step()

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
        self.next_step()

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


class HuntAndKill(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        self.grid = grid

        self.unvisited_legit_cells = []

        self.expeditions = 2

        self.direction = - 1

        self.unvisited_legit_cells = []
        if self.must_break():
            return
        self.set_current(self.grid.random_cell(self._seed))

        self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())

        while self.current and not self.must_break():
            while self.current and not self.must_break():
                neighbor, self.direction = self.current.get_biased_unmasked_unlinked_directional_neighbor(self.bias, self.direction)
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                    if self.must_break():
                        break
                else:
                    self.current = None
            if self.must_break():
                break
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)

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
        self.next_step()

    def set_current(self, c):
        self.current = c
        c.group = self.expeditions
        unvisited_neighbors = self.current.get_unlinked_neighbors()
        self.add_to_unvisited_legit_cells(unvisited_neighbors)

    def add_to_unvisited_legit_cells(self, visited_cells):
        self.unvisited_legit_cells.extend([c for c in visited_cells if c not in self.unvisited_legit_cells])


class RecursiveBacktracker(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=0, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        expeditions = 1

        stack = [grid.random_cell(_seed)]
        stack[-1].group = expeditions + 1

        backtracking = False
        direction = - 1

        while len(stack) > 0 and not self.must_break():
            current = stack[-1]

            unlinked_neighbor, direction = current.get_biased_unmasked_unlinked_directional_neighbor(bias, direction)
            if unlinked_neighbor:
                current.link(unlinked_neighbor)
                self.next_step()
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


class Sidewinder(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)
        self.bias = (bias + 1) / 2

        for row in grid.each_row():
            run = []
            for c in row:
                if self.must_break():
                    break
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

                self.next_step()

        self.color_cells_by_tree_root(grid.each_cell())

    def must_close_run(self):
        return self.bias > random()


class Wilson(MazeAlgorithm):
    def __init__(self, grid, _seed, _max_steps=-1, bias=0):
        super().__init__(_seed=_seed, _max_steps=_max_steps, bias=bias)

        unvisited = grid.get_unmasked_cells().copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0 and not self.must_break():
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited and not self.must_break():
                cell = choice([c for c in cell.get_neighbors() if c != path[-1]])
                try:
                    path = path[0:path.index(cell) + 1]
                except ValueError:
                    path.append(cell)
                self.next_step()

            for i in range(0, len(path) - 1):
                path[i].link(path[i + 1])
                path[i].group = 1
                path[i + 1].group = 1
                unvisited.remove(path[i])
            self.next_step()


class Eller(MazeAlgorithm):
    def __init__(self, grid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        for row in grid.each_row():
            if self.must_break():
                break
            tree_roots_this_row = {}
            for c in row:
                this_root = c.get_root()
                if self.must_break():
                    break
                if c.neighbors[3] and (c.row == grid.rows - 1 or (self.bias < random() and not c.is_same_tree(c.neighbors[3]))):
                    c.link(c.neighbors[3])
                    self.next_step()
                try:
                    tree_roots_this_row[this_root] = [c]
                except IndexError:
                    tree_roots_this_row[this_root].append(c)

            if c.row != grid.rows - 1:
                for tree, cells in tree_roots_this_row.items():
                    for c in choices(cells, k=min(len(cells), max(1, round((random() + self.bias - 0.5) * len(cells))))):
                        if self.must_break():
                            break
                        if c.neighbors[0]:
                            c.link(c.neighbors[0])
                            self.next_step()

        self.color_cells_by_tree_root(grid.each_cell())


class KruskalRandom(MazeAlgorithm):
    def __init__(self, grid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = grid

        if hasattr(grid, 'weave'):
            potential_passages = []
            for c in range(1, grid.columns - 1):
                for r in range(1, grid.rows - 1):
                    potential_passages.append(grid[c, r])
            shuffle(potential_passages)

            for pp in potential_passages[0: round(grid.weave * len(potential_passages))]:
                self.add_crossing(pp)

        unvisited_cells = grid.shuffled_cells()
        for c in unvisited_cells:
            if self.must_break():
                break
            [(c.link(n), self.next_step()) for n in c.get_biased_unmasked_neighbors(self.bias) if not c.is_same_tree(n)]
        self.color_cells_by_tree_root(unvisited_cells)

    def add_crossing(self, cell):
        can_cross = not cell.has_any_link() and not cell.neighbors[1].is_same_tree(cell.neighbors[3]) and not cell.neighbors[0].is_same_tree(cell.neighbors[2])
        if not can_cross:
            return False

        if random() > 0.5:  # Vertical underway
            cell.link(cell.neighbors[1])
            cell.link(cell.neighbors[3])

            self.grid.tunnel_under(cell)

            cell.neighbors[0].link(cell.neighbors[0].neighbors[cell.neighbors_return[0]])
            cell.neighbors[2].link(cell.neighbors[2].neighbors[cell.neighbors_return[2]])
        else:
            cell.link(cell.neighbors[0])
            cell.link(cell.neighbors[2])

            self.grid.tunnel_under(cell)

            cell.neighbors[1].link(cell.neighbors[1].neighbors[cell.neighbors_return[1]])
            cell.neighbors[3].link(cell.neighbors[3].neighbors[cell.neighbors_return[3]])

        return True
