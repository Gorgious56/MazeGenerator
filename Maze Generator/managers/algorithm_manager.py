from random import seed, choice, choices, random, shuffle, randrange
from math import ceil, hypot
from ..utils . priority_queue import PriorityQueue
from .cell_type_manager import POLAR, SQUARE
from ..utils . union_find import UnionFind
from ..utils import methods
from ..maze_logic import constants as cst
from . import space_rep_manager as sp_mgr


def work(grid, props):
    try:
        ALGORITHM_FROM_NAME[props.maze_algorithm](grid, props)
    except KeyError:
        pass


class MazeAlgorithm(object):
    name = 'NOT REGISTERED'
    weaved = True
    settings = ['maze_bias', 'maze_weave']

    def __init__(self, grid=None, props=None):
        self.grid = grid
        self.bias = props.maze_bias
        self._seed = props.seed
        seed(self._seed)

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

    def color_cells_by_tree_root(self):
        try:
            union_find = getattr(self, 'union_find')
            links = []
            for c in self.grid.all_cells:
                link = union_find.find(c)
                if link:
                    try:
                        c.group = links.index(link)
                    except ValueError:
                        links.append(link)
                        c.group = len(links) - 1
        except AttributeError:
            print('No Union Find Algorithm declared for this algorithm')

    def add_crossing(self, cell):
        grid = self.grid
        can_cross = not cell.has_any_link()
        if can_cross:
            north = cell.neighbor(cst.NORTH)
            west = cell.neighbor(cst.WEST)
            south = cell.neighbor(cst.SOUTH)
            east = cell.neighbor(cst.EAST)
            if random() > 0.5:  # Vertical underway
                grid.link(cell, west)
                self.union_find.union(cell, west)
                grid.link(cell, east)
                self.union_find.union(cell, east)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                grid.link(north, north.neighbor(cell.get_neighbor_return(cst.NORTH)))
                self.union_find.union(north, north.neighbor(cell.get_neighbor_return(cst.NORTH)))
                grid.link(south, south.neighbor(cell.get_neighbor_return(cst.SOUTH)))
                self.union_find.union(south, south.neighbor(cell.get_neighbor_return(cst.SOUTH)))
            else:
                grid.link(cell, north)
                self.union_find.union(cell, north)
                grid.link(cell, south)
                self.union_find.union(cell, south)

                new_cell_under = self.grid.tunnel_under(cell)
                self.union_find.data[new_cell_under] = new_cell_under

                grid.link(west, west.neighbor(cell.get_neighbor_return(cst.WEST)))
                self.union_find.union(west, west.neighbor(cell.get_neighbor_return(cst.WEST)))
                grid.link(east, east.neighbor(cell.get_neighbor_return(cst.EAST)))
                self.union_find.union(east, east.neighbor(cell.get_neighbor_return(cst.EAST)))
            return True
        return False


class BinaryTree(MazeAlgorithm):
    """
    One of the most simple algorithms

    A strong diagonal texture.
    Mandatory corridors along the Top and Right of the maze
    """
    name = 'Binary Tree'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.union_find = UnionFind(self.grid.all_cells)
        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        bias = self.bias
        for c in grid.all_cells:
            neighbors = []
            east_neighbor = grid.next_column(c)
            columns_this_row = grid.get_columns_this_row(c.row)
            if east_neighbor and east_neighbor in c.neighbors and c.column < columns_this_row - 1:
                neighbors.append(east_neighbor)
            if not east_neighbor or c.row < grid.rows - 1:
                next_row = grid.next_row(c)
                if next_row in c.neighbors:
                    neighbors.append(next_row)
                elif c.column == columns_this_row - 1:
                    prev_column = grid.previous_column(c)
                    if prev_column:
                        grid.link(c, prev_column)
                        c = prev_column
                        neighbors = [grid.next_row(c)]
            if grid.levels > 1 and c.row == self.grid.rows - 1:
                next_level = grid.next_level(c)
                if next_level in c.neighbors:
                    neighbors.append(next_level)
            if not neighbors:
                continue
            link_neighbor = methods.get_biased_choices(neighbors, bias, 5)[0]
            if not self.union_find.connected(c, link_neighbor):
                grid.link(c, link_neighbor)
                self.union_find.union(c, link_neighbor)


class Sidewinder(MazeAlgorithm):
    """
    Simple algorithm

    A strong vertical texture.
    Mandatory corridor along the Top of the maze
    """
    name = 'Sidewinder'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells)

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        for row in grid.each_row():
            run = []
            for c in row:
                run.append(c)
                east_neighbor = grid.next_column(c)
                link_north = False
                if not east_neighbor or c.column == grid.get_columns_this_row(c.row) - 1 or (grid.next_row(c) and self.must_close_run()):
                    shuffle(run)
                    for member in run:
                        next_row = grid.next_row(member)
                        if next_row and next_row in member.neighbors:
                            grid.link(member, next_row)
                            run = []
                            link_north = True
                            break
                if not link_north:
                    if east_neighbor:
                        grid.link(c, east_neighbor)
                    else:
                        grid.link(c, grid.previous_column(c))

    def must_close_run(self):
        return self.bias > random()


class Eller(MazeAlgorithm):
    """
    Simple algorithm

    No particular texture.
    Generates a lot of dead-ends.
    """
    name = 'Eller'
    weaved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells)

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        uf = self.union_find
        grid = self.grid
        for row in grid.each_row():
            sets_this_row = {}
            for c in row:
                next_col = grid.next_column(c)
                if next_col and ((c.row == grid.rows - 1 or self.bias < random()) and not uf.connected(c, next_col)):
                    grid.link(c, next_col)
                    uf.union(c, next_col)
            for c in row:
                this_set = uf.find(c)
                if this_set in sets_this_row:
                    sets_this_row[this_set].append(c)
                else:
                    sets_this_row[this_set] = [c]

            for tree, cells in sets_this_row.items():
                ch_len = min(len(cells), randrange(1, ceil(self.bias * len(cells) + 2)))
                for c in choices(cells, k=ch_len):
                    neigh = grid.next_row(c)
                    if neigh not in c.neighbors:
                        other_col = grid.next_column(c)
                        if not other_col:
                            other_col = grid.previous_column(c)
                        grid.link(other_col, grid.next_row(other_col))
                        uf.union(other_col, grid.next_row(other_col))
                        neigh = other_col
                    if neigh:
                        grid.link(c, neigh)
                        uf.union(c, neigh)


class CrossStitch(MazeAlgorithm):
    """
    Variation to the Sidewinder

    Strong diagonal texture from the central point.
    """
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
            unvisited_neighbor, direction = self.current.get_biased_unlinked_directional_neighbor(self.bias, direction)

            if unvisited_neighbor:
                self.link_to(self.current, unvisited_neighbor)
                self.set_current(unvisited_neighbor)
            else:
                self.set_current(None)

            while self.unvisited_legit_cells:
                c = self.unvisited_legit_cells[0]
                if not c.has_any_link():
                    neighbor = methods.get_biased_choices(c.get_linked_neighbors(), self.bias)[0]
                    if neighbor:
                        self.set_current(c)
                        self.link_to(self.current, neighbor)

    def link_to(self, c, other_c):
        self.grid.link(c, other_c)
        if other_c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(other_c)
        if c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(c)
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
    settings = ['maze_bias', 'maze_weave']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.union_find = UnionFind(self.grid.all_cells)

        self.add_template_passages()

        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        grid = self.grid
        unvisited_cells = grid.shuffled_cells()
        for c in unvisited_cells:
            for n in methods.get_biased_choices(c.neighbors, self.bias, k=len(c.neighbors)):
                if not self.union_find.connected(c, n):
                    link_a, link_b = grid.link(c, n)  # Keep this because of the weave maze
                    self.union_find.union(link_a, link_b)


class Prim(MazeAlgorithm):
    name = 'Prim'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bias = round((1 - abs(self.bias)) * 10)

        self.union_find = UnionFind(self.grid.all_cells)

        self.q = PriorityQueue()
        self.run()
        self.color_cells_by_tree_root()

    def run(self):
        start_cell = self.grid.random_cell()
        self.push_to_queue(start_cell)

        while not self.q.is_empty():
            cell, neighbor = self.q.pop()
            if not self.union_find.connected(cell, neighbor):
                self.grid.link(cell, neighbor)
                self.union_find.union(cell, neighbor)
                self.push_to_queue(neighbor)
            self.push_to_queue(cell)

    def push_to_queue(self, cell):
        try:
            self.q.push((cell, choice(cell.get_unlinked_neighbors())), randrange(0, self.bias + 1))
        except IndexError:
            pass


class GrowingTree(MazeAlgorithm):
    name = 'Growing Tree'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.run()

    def run(self):
        active_cells = [self.grid.random_cell()]

        while active_cells:
            cell = choice(list(reversed(active_cells))[0:int(len(active_cells) * self.bias) + 1])
            unlinked_neighbors = cell.get_unlinked_neighbors()
            if unlinked_neighbors:
                available_neighbor = choice(unlinked_neighbors)
                self.grid.link(cell, available_neighbor)
                active_cells.append(available_neighbor)
            else:
                active_cells.remove(cell)


class RecursiveDivision(MazeAlgorithm):
    name = 'Recursive Division'
    weaved = False
    settings = ['maze_bias']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)
        self.bias = (self.bias + 1) / 2

        self.union_find = UnionFind(self.grid.all_cells)

        self.run()

        self.color_cells_by_tree_root()

    def run(self):
        self.divide(0, 0, self.grid.rows, self.grid.columns)

    def divide(self, mx, my, ax, ay):
        HORIZONTAL, VERTICAL = 0, 1
        grid = self.grid

        dx = ax - mx
        dy = ay - my
        if dx < 2 or dy < 2:
            # make a hallway
            if dx > 1:
                y = my
                for x in range(mx, ax):
                    self.link(grid[y, x], 2)
            elif dy > 1:
                x = mx
                for y in range(my, ay):
                    self.link(grid[y, x], 3)
            return

        wall = HORIZONTAL if dy > dx else (VERTICAL if dx > dy else randrange(2))

        xp = methods.get_biased_choices(list(range(mx, ax - (wall == VERTICAL))), self.bias)[0]
        yp = methods.get_biased_choices(list(range(my, ay - (wall == HORIZONTAL))), self.bias)[0]

        if wall == HORIZONTAL:
            nx, ny = ax, yp + 1
            neighbor = 3
            ox, oy = mx, ny
        else:
            nx, ny = xp + 1, ay
            neighbor = 2
            ox, oy = nx, my
        self.link(grid[yp, xp], neighbor)

        self.divide(mx, my, nx, ny)
        self.divide(ox, oy, ax, ay)

    def link(self, cell, neighbor_number):
        if cell:
            n = cell.neighbor(neighbor_number)
            if n and not self.union_find.connected(cell, n):
                self.grid.link(cell, n)
                self.union_find.union(cell, n)
                return True
        return False


class RecursiveVoronoiDivision(MazeAlgorithm):
    name = 'Recursive Voronoi Division'
    settings = ['maze_room_size', 'maze_room_size_deviation']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.maze_room_size
        self.room_size_deviation = props.maze_room_size_deviation

        self.expeditions = 0

        all_cells = self.grid.all_cells.copy()

        # Destroy all walls:
        [[grid.link(c, n, False) for n in c.neighbors if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        # Interpretation of https://rosettacode.org/wiki/Voronoi_diagram#Python with two points
        # Could use actual sets for the data at the cost of determinism
        if len(cells) <= max(2, randrange(int(self.room_size * (1 - (self.room_size_deviation / 100))), self.room_size + 1)):
            return

        # Choose two cells at random
        c_a, c_b = cells.pop(randrange(0, len(cells))), cells.pop(randrange(0, len(cells)))

        set_a, set_b, frontier = [c_a], [c_b], []

        # Build the voronoi diagram : Each set will contain the cell if it is closest to one of the randomly chosen point
        # There is a slight bias toward set_b but the calculation save is worth it
        [(set_a if hypot(c.column - c_a.column, c.row - c_a.row) < hypot(c.column - c_b.column, c.row - c_b.row) else set_b).append(c) for c in cells]

        # Add the frontier walls to a container
        [[frontier.append((c_set_a, c_set_b)) for c_set_b in [_n for _n in c_set_a.neighbors if _n in set_b]] for c_set_a in set_a]

        union_find_a = UnionFind(set_a)
        union_find_b = UnionFind(set_a)

        for c in set_a:
            c.group = self.expeditions
            for n in [n for n in c.neighbors if n in set_a]:
                union_find_a.union(c, n)
        for c in set_b:
            c.group = self.expeditions
            for n in [n for n in c.neighbors if n in set_b]:
                union_find_b.union(c, n)
        self.expeditions += 1

        # Unlink all the cells in the frontier but one
        if len(frontier) > 0:
            actual_psg = frontier.pop(randrange(0, len(frontier)))
            self.grid.link(actual_psg[0], actual_psg[1])
            for psg in frontier:
                # Make sure we don't close dead-ends or cells which got isolated from their set
                if len(psg[0].links) > 1 \
                        and len(psg[1].links) > 1\
                        and union_find_a.connected(psg[0], c_a) \
                        and union_find_b.connected(psg[1], c_b):
                    psg[0].unlink(psg[1])
            [self.run(s_x) for s_x in (set_a, set_b)]


class VoronoiDivision(MazeAlgorithm):
    name = 'Voronoi Division'
    settings = ['maze_room_size']

    def __init__(self, grid, props=None, *args, **kwargs):
        super().__init__(grid=grid, props=props, *args, **kwargs)

        self.room_size = props.maze_room_size
        self.room_size_deviation = props.maze_room_size_deviation
        self.rooms = grid.size // self.room_size

        all_cells = self.grid.all_cells.copy()

        shuffle(all_cells)
        self.union_find = UnionFind(all_cells)

        self.room_centers = all_cells[0:self.rooms]

        self.expeditions = 0

        # Destroy all walls:
        [[grid.link(c, n, False) for n in c.neighbors if n.level == c.level] for c in all_cells]
        self.run(all_cells)

    def run(self, cells):
        union_find = self.union_find

        frontiers = []
        [frontiers.append({}) for room in range(self.rooms)]

        for c in self.grid.all_cells:
            dmin = 100000000
            j = -1
            for i, r_c in enumerate(self.room_centers):
                d = hypot(r_c.column - c.column, r_c.row - c.row)
                if d < dmin:
                    dmin = d
                    j = i
            if j >= 0:
                union_find.union(c, self.room_centers[j])
                c.group = j

        cell_centers_union_groups = [union_find.find(c) for c in self.room_centers]

        for c in self.grid.all_cells:
            for n in [n for n in c.neighbors if not union_find.connected(c, n)]:
                try:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][cell_centers_union_groups.index(union_find.find(n))].append((c, n))
                except KeyError:
                    frontiers[cell_centers_union_groups.index(union_find.find(c))][cell_centers_union_groups.index(union_find.find(n))] = [(c, n)]

        linked_cells = []
        for frontier_dic in frontiers:
            for ind, frontier in frontier_dic.items():
                already_open = False
                for lc in linked_cells:
                    if lc in frontier:
                        linked_cells.remove(lc)
                        already_open = True
                if frontier and not already_open:
                    actual_psg = frontier[randrange(0, len(frontier))]
                    if not union_find.connected(actual_psg[0], actual_psg[1]):
                        frontier.remove(actual_psg)
                        union_find.union(actual_psg[0], actual_psg[1])
                        linked_cells.append((actual_psg[1], actual_psg[0]))
                    for link in [link for link in frontier if len(link[0].links) > 1 and len(link[1].links) > 1]:
                        link[0].unlink(link[1])


class AldousBroder(MazeAlgorithm):
    name = 'Aldous-Broder'
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        expeditions = 1
        current = grid.random_cell(self._seed)
        current.group = expeditions

        unvisited = grid.size - 1 - grid.masked_cells
        while unvisited > 0:

            neighbor = choice(current.neighbors)

            if len(neighbor.links) <= 0:
                grid.link(current, neighbor)
                unvisited -= 1
            current = neighbor
            current.group = expeditions


class Wilson(MazeAlgorithm):
    name = 'Wilson'
    settings = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grid = self.grid

        unvisited = grid.all_cells.copy()
        target_cell = choice(unvisited)
        unvisited.remove(target_cell)
        target_cell.group = -1

        while len(unvisited) > 0:
            cell = choice(unvisited)
            cell.group = 1
            path = [cell]

            while cell in unvisited:
                cell = choice([c for c in cell.neighbors if c != path[-1]])
                try:
                    path = path[0:path.index(cell) + 1]
                except ValueError:
                    path.append(cell)

            for i in range(0, len(path) - 1):
                grid.link(path[i], path[i + 1])
                path[i].group = 1
                path[i + 1].group = 1
                unvisited.remove(path[i])


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
                neighbor, self.direction = self.current.get_biased_unlinked_directional_neighbor(self.bias, self.direction)
                if neighbor:
                    self.link_to(self.current, neighbor)
                    self.set_current(neighbor)
                else:
                    self.current = None
            try:
                self.expeditions += 1
                self.set_current(choice(self.unvisited_legit_cells))
                neighbor = choice(self.current.get_linked_neighbors())
                self.link_to(neighbor, self.current)

                self.direction = neighbor.get_neighbor_direction(self.current)

                self.add_to_unvisited_legit_cells(self.current.get_unlinked_neighbors())
            except IndexError:  # Neighbors is empty
                break

    def link_to(self, c, other_c):
        self.grid.link(c, other_c)
        if other_c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(other_c)
        if c in self.unvisited_legit_cells:
            self.unvisited_legit_cells.remove(c)

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

            unlinked_neighbor, direction = current.get_biased_unlinked_directional_neighbor(self.bias, direction)
            if unlinked_neighbor:
                self.grid.link(current, unlinked_neighbor)
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

WEAVED_ALGORITHMS = [algo.name for algo in ALGORITHMS if algo.weaved]


def is_algo_incompatible(props):
    if ALGORITHM_FROM_NAME[props.maze_algorithm] == AldousBroder and props.maze_space_dimension == sp_mgr.REP_BOX:
        return "Aldous-Broder can't solve a box representation"
    if props.maze_space_dimension == sp_mgr.REP_BOX and props.maze_weave:
        return "Can't solve weaved maze for a box"
    if ALGORITHM_FROM_NAME[props.maze_algorithm] in (RecursiveDivision, VoronoiDivision) and props.cell_type == POLAR:
        return "Can't solve this algorithm with Polar grid (yet)"
    return False


def is_algo_weaved(props):
    return props.cell_type == SQUARE and props.maze_algorithm in WEAVED_ALGORITHMS


def is_kruskal_random(algo_name):
    return algo_name == KruskalRandom.name


def generate_algo_enum():
    return [(alg_name, alg_name, '') for alg_name in ALGORITHMS_NAMES]
