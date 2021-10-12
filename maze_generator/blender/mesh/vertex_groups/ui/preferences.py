def draw(layout, mg_props):
    props_vg = mg_props.meshes.vertex_groups
    for attr in props_vg.attributes_names:
        layout.prop(props_vg, attr)
