import bpy

scene = bpy.context.scene
render = scene.render
directory = render.filepath

for i in range(scene.frame_start, scene.frame_end):
    scene.frame_set(i)
    render.filepath = f"{directory}{i:05d}"
    bpy.ops.render.render(write_still=True)

render.filepath = directory
