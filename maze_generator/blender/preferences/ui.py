import bpy
from maze_generator.blender.preferences.constants import addon_name

from maze_generator.blender.mesh.vertex_groups.preferences import VertexGroupsNamesPG
from maze_generator.blender.collection.preferences import CollectionsNamesPG
from maze_generator.blender.object.preferences import ObjectsNamesPG


class PreferencesToggles(bpy.types.PropertyGroup):
    state: bpy.props.BoolProperty()
    name: bpy.props.StringProperty()


def get_or_create(toggles, attr):
    for t in toggles:
        if t.name == attr:
            return t
    new = toggles.add()
    new.name = attr
    new.state = False
    return new


class MazeGeneratorPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_name

    pref_context: bpy.props.EnumProperty(
        items=(
            ("Collection",) * 3,
            ("Objects",) * 3,
            ("Vertex Groups",) * 3,
        )
    )
    vertex_groups_names: bpy.props.PointerProperty(type=VertexGroupsNamesPG)
    collections_names: bpy.props.PointerProperty(type=CollectionsNamesPG)
    objects_names: bpy.props.PointerProperty(type=ObjectsNamesPG)
    toggles: bpy.props.CollectionProperty(type=PreferencesToggles)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Addon Defaults")
        layout.row().prop_tabs_enum(self, "pref_context")

        if self.pref_context == "Collection":
            self.fold_section("collections_names", "Collections Names")
        elif self.pref_context == "Vertex Groups":
            self.fold_section("vertex_groups_names", "Vertex Groups Names")
        elif self.pref_context == "Objects":
            self.fold_section("objects_names", "Objects Names")

    def fold_section(self, attr, label):
        toggle = get_or_create(self.toggles, attr)
        box = self.layout.box()
        row = box.row(align=True)
        row.prop(
            toggle,
            "state",
            toggle=True,
            icon="DISCLOSURE_TRI_DOWN" if toggle.state else "DISCLOSURE_TRI_RIGHT",
            text=label,
            emboss=False,
        )
        if toggle.state:
            for _attr in getattr(self, attr).attributes_names:
                box.prop(getattr(self, attr), _attr)
