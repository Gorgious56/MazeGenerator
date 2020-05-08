from ..maze_logic import grids
from ..managers import cell_type_manager as ct
from ..managers import space_rep_manager as sp_rep
from ..managers import algorithm_manager


class GridManager:
    grid = None

    def generate_grid(props) -> None:
        self = GridManager

        grid = None
        maze_dimension = int(props.maze_space_dimension)
        if props.cell_type == ct.POLAR:
            grid = grids.GridPolar
        elif props.cell_type == ct.HEXAGON:
            grid = grids.GridHex
        elif props.cell_type == ct.TRIANGLE:
            grid = grids.GridTriangle
        elif props.cell_type == ct.OCTOGON:
            grid = grids.GridOctogon
        elif props.cell_type == ct.DODECAGON:
            grid = grids.GridDodecagon
        else:
            if props.maze_weave:
                self.grid = grids.GridWeave(
                    rows=props.maze_rows_or_radius,
                    columns=props.maze_columns,
                    levels=1,
                    cell_size=1 - max(0.2, props.cell_inset),
                    use_kruskal=algorithm_manager.is_kruskal_random(props.maze_algorithm),
                    weave=props.maze_weave,
                    space_rep=maze_dimension)
                return
            elif maze_dimension == int(sp_rep.REP_BOX):
                rows = props.maze_rows_or_radius
                cols = props.maze_columns
                self.grid = grids.Grid(
                    rows=3 * rows,
                    columns=2 * cols + 2 * rows,
                    levels=props.maze_levels if maze_dimension == int(sp_rep.REP_REGULAR) else 1,
                    cell_size=1 - props.cell_inset,
                    space_rep=maze_dimension,
                    mask=[
                        (0, 0, rows - 1, rows - 1),
                        (rows + cols, 0, 2 * rows + 2 * cols - 1, rows - 1),
                        (0, 2 * rows, rows - 1, 3 * rows - 1),
                        (rows + cols, 2 * rows, 2 * rows + 2 * cols - 1, 3 * rows - 1)])
                return
            else:
                grid = grids.Grid
        self.grid = grid(
            rows=props.maze_rows_or_radius,
            columns=props.maze_columns,
            levels=props.maze_levels if maze_dimension == int(sp_rep.REP_REGULAR) else 1,
            cell_size=1 - props.cell_inset,
            space_rep=maze_dimension)
