import bmesh
import bpy
from mathutils import Vector


def remove_all_vertex_layers(mesh):
    vertex_colors = mesh.vertex_colors
    while vertex_colors:
        vertex_colors.remove(vertex_colors[0])


def set_mesh_layers(obj, cells_visual):
    mesh = obj.data
    remove_all_vertex_layers(mesh)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    color_tables = {}
    color_layers = {}
    # colors_layers = []
    for layer_name in cells_visual[0].color_layers:
        color_tables[layer_name] = []
        color_layers[layer_name] = bm.loops.layers.color.new(layer_name)
    for cv in cells_visual:
        for layer, color in cv.color_layers.items():
            for f in cv.faces:
                color_tables[layer].extend([color] * f.corners())

    for layer_name in color_layers:
        color_layer = color_layers[layer_name]
        color_table = color_tables[layer_name]
        for face in bm.faces:
            for loop in face.loops:
                loop[color_layer] = color_table[loop.vert.index]

    # newGeom = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    # verts = [e for e in newGeom['geom'] if isinstance(e, bmesh.types.BMVert)]
    # bmesh.ops.translate(bm, vec=Vector((0, 0, -1)), verts=verts)z

    bm.to_mesh(mesh)