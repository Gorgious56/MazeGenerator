"""
Grid creation manager
"""


from maze_generator.maze.cell.constants import CellType as ct
from maze_generator.maze.space_representation.constants import SpaceRepresentation
from .polar import GridPolar
from .hex import GridHex
from .triangle import GridTriangle
from .octogon import GridOctogon
from .dodecagon import GridDodecagon
from .weave import GridWeave
from .box import GridBox
from .grid import Grid
from maze_generator.maze.algorithm.algorithms import is_kruskal_random


def generate_grid(props) -> None:
    grid = None
    maze_dimension = props.space_rep_props.representation
    warp_horiz = maze_dimension in (
        SpaceRepresentation.CYLINDER.value,
        SpaceRepresentation.MOEBIUS.value,
        SpaceRepresentation.TORUS.value,
    )
    warp_vert = maze_dimension == SpaceRepresentation.TORUS.value
    cell_props = props.cell_props
    if cell_props.is_a(ct.POLAR):
        return GridPolar(
            rows=props.maze_rows_or_radius,
            columns=0,
            levels=props.maze_levels,
            cell_size=1 - props.cell_props.inset,
            branch_polar=props.maze_polar_branch,
        )

    if cell_props.is_a(ct.HEXAGON):
        grid = GridHex
    elif cell_props.is_a(ct.TRIANGLE):
        grid = GridTriangle
    elif cell_props.is_a(ct.OCTOGON):
        grid = GridOctogon
    elif cell_props.is_a(ct.DODECAGON):
        grid = GridDodecagon
    else:
        if props.maze_weave:
            return GridWeave(
                rows=props.maze_rows_or_radius,
                columns=props.maze_columns,
                levels=1,
                cell_size=1 - max(0.2, props.cell_props.inset),
                use_kruskal=is_kruskal_random(props.algorithm.algorithm),
                weave=props.maze_weave,
                warp_horiz=warp_horiz,
                warp_vert=warp_vert,
            )

        if maze_dimension == SpaceRepresentation.BOX.value:
            rows = props.maze_rows_or_radius
            cols = props.maze_columns
            return GridBox(
                rows=3 * rows,
                columns=2 * cols + 2 * rows,
                levels=props.maze_levels,
                cell_size=1 - props.cell_props.inset,
                mask=[
                    (0, 0, rows - 1, rows - 1),
                    (rows + cols, 0, 2 * rows + 2 * cols - 1, rows - 1),
                    (0, 2 * rows, rows - 1, 3 * rows - 1),
                    (rows + cols, 2 * rows, 2 * rows + 2 * cols - 1, 3 * rows - 1),
                ],
            )
        grid = Grid
    return grid(
        rows=props.maze_rows_or_radius,
        columns=props.maze_columns,
        levels=props.maze_levels,
        cell_size=1 - props.cell_props.inset,
        warp_horiz=warp_horiz,
        warp_vert=warp_vert,
    )
