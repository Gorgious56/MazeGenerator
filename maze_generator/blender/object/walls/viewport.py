def update_wall_visibility(props, is_algo_weaved) -> None:
    obj_walls = props.objects.walls
    obj_walls.hide_viewport = obj_walls.hide_render = props.wall_hide or (props.maze_weave and is_algo_weaved)
