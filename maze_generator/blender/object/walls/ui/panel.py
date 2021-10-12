"""
Walls Panel
"""
import bpy


class WallsPanel(bpy.types.Panel):
    """
    Walls Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_WallPanel"
    bl_label = " "
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene.mg_props.objects.walls

    def draw_header(self, context):
        self.layout.label(text="Walls", icon="SNAP_EDGE")
        wall_hide = context.scene.mg_props.wall_hide
        self.layout.prop(context.scene.mg_props, "wall_hide", text="", icon="HIDE_ON" if wall_hide else "HIDE_OFF")

    def draw(self, context):
        layout = self.layout

        mg_props = context.scene.mg_props
        mod_names = mg_props.mod_names

        obj_walls = mg_props.objects.walls
        if obj_walls:
            try:  # TODO get rid of try/except
                row = layout.row(align=True)
                wall_bevel_mod = obj_walls.modifiers.get(mod_names.bevel)
                if wall_bevel_mod:
                    layout.prop(wall_bevel_mod, "width", text="Bevel")
                wall_screw_mod = obj_walls.modifiers.get(mod_names.screw)
                if wall_screw_mod:
                    row.prop(wall_screw_mod, "screw_offset", text="Height")
                wall_solid_mod = obj_walls.modifiers.get(mod_names.solid)
                if wall_solid_mod:
                    row.prop(wall_solid_mod, "thickness")
            except ReferenceError:
                pass

        wall_mat = mg_props.display.materials.wall
        if wall_mat:
            for n in wall_mat.node_tree.nodes:
                if not isinstance(n, bpy.types.ShaderNodeBsdfPrincipled):
                    continue
                layout.prop(n.inputs[0], "default_value", text="Color")
                break
