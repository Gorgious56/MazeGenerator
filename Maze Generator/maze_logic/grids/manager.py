"""
Grid creation manager
"""


from .. import cells as ct
from .polar import GridPolar
from .hex import GridHex
from .triangle import GridTriangle
from .octogon import GridOctogon
from .dodecagon import GridDodecagon
from .weave import GridWeave
from .box import GridBox
from .grid import Grid
from ..algorithms import manager as algorithm_manager


def generate_grid(props) -> None:
    grid = None
    maze_dimension = props.maze_space_dimension
    space_reps = props.space_reps
    warp_horiz = maze_dimension in (space_reps.cylinder, space_reps.moebius, space_reps.torus)
    warp_vert = maze_dimension == space_reps.torus
    if props.cell_type == ct.POLAR:
        return GridPolar(
            rows=props.maze_rows_or_radius,
            columns=0,
            levels=props.maze_levels,
            cell_size=1 - props.cell_inset,
            branch_polar=props.maze_polar_branch)

    if props.cell_type == ct.HEXAGON:
        grid = GridHex
    elif props.cell_type == ct.TRIANGLE:
        grid = GridTriangle
    elif props.cell_type == ct.OCTOGON:
        grid = GridOctogon
    elif props.cell_type == ct.DODECAGON:
        grid = GridDodecagon
    else:
        if props.maze_weave:
            return GridWeave(
                rows=props.maze_rows_or_radius,
                columns=props.maze_columns,
                levels=1,
                cell_size=1 - max(0.2, props.cell_inset),
                use_kruskal=algorithm_manager.is_kruskal_random(
                    props.maze_algorithm),
                weave=props.maze_weave,
                warp_horiz=warp_horiz,
                warp_vert=warp_vert,
                )

        if maze_dimension == space_reps.box:
            rows = props.maze_rows_or_radius
            cols = props.maze_columns
            return GridBox(
                rows=3 * rows,
                columns=2 * cols + 2 * rows,
                levels=props.maze_levels,
                cell_size=1 - props.cell_inset,
                mask=[
                    (0, 0, rows - 1, rows - 1),
                    (rows + cols, 0, 2 * rows + 2 * cols - 1, rows - 1),
                    (0, 2 * rows, rows - 1, 3 * rows - 1),
                    (rows + cols, 2 * rows, 2 * rows + 2 * cols - 1, 3 * rows - 1)])
        grid = Grid
    return grid(
        rows=props.maze_rows_or_radius,
        columns=props.maze_columns,
        levels=props.maze_levels,
        cell_size=1 - props.cell_inset,
        warp_horiz=warp_horiz,
        warp_vert=warp_vert,
        )
