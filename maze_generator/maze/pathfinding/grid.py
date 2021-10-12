from maze_generator.maze.pathfinding.distance import Distances


def calc_distances(grid, props):
    if props.path.solution == "Random":
        if props.path.force_outside:
            start_cell, end_cell = grid.get_outer_cells()
        else:
            start_cell = grid.random_cell()
            end_cell = grid.random_cell()
        setattr(grid, "start_cell", start_cell)
        setattr(grid, "end_cell", end_cell)
        grid.distances = Distances(start_cell)
        grid.longest_path = grid.distances.path_to(end_cell).path
    elif props.path.solution == "Custom":
        start_cell = grid[min(props.path.start[0], grid.columns - 1), min(props.path.start[1], grid.rows - 1)]
        end_cell = grid[min(props.path.end[0], grid.columns - 1), min(props.path.end[1], grid.rows - 1)]
        setattr(grid, "start_cell", start_cell)
        setattr(grid, "end_cell", end_cell)
        grid.distances = Distances(start_cell)
        grid.longest_path = grid.distances.path_to(end_cell).path
    else:  # Longest path possible
        distances = Distances(grid.get_random_linked_cell(_seed=props.algorithm.seed))
        new_start, distance = distances.max
        distances = Distances(new_start)
        goal, max_distance = distances.max

        longest_path = distances.path_to(goal).path
        if longest_path and longest_path[0] is not None:
            # Avoid flickering when the algorithm randomly chooses start and end cells.
            start = longest_path[0]
            start = (start.row, start.column, start.level)
            last_start = props.path.last_start_cell
            last_start = (last_start[0], last_start[1], last_start[2])
            if start != last_start:
                goal = longest_path[-1]
                goal = (goal.row, goal.column, goal.level)
                if goal == last_start:
                    distances.reverse()
                else:
                    props.path.last_start_cell = start
            # End.
        grid.distances = distances
        grid.longest_path = longest_path
