import bpy
from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntVectorProperty,
)
from maze_generator.blender.mesh.constants import (
    CELL_VISUAL_ENUM,
    DEFAULT_CELL_VISUAL_TYPE,
)
from maze_generator.blender.shading.material.main import update_links
from maze_generator.blender.shading.material.prop import MaterialsPropertyGroup


def update_paint(self, context: bpy.types.Context) -> None:
    mg_props = context.scene.mg_props
    update_links(mg_props)
    if not self.show_longest_path:
        mg_props.objects.cells.modifiers[mg_props.mod_names.mask_longest_path].show_viewport = False


class DisplayPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing display parameters
    """
    materials: PointerProperty(type=MaterialsPropertyGroup)

    seed_color: IntProperty(
        name="Color Seed",
        description="Configure the wall default width",
    )

    show_longest_path: BoolProperty(
        name="Longest Path",
        description="Toggle this property to show the longest path",
        default=False,
        update=update_paint,
    )

    paint_style: EnumProperty(
        name="Paint Style",
        description="Choose how to paint the cells",
        items=CELL_VISUAL_ENUM,
        default=DEFAULT_CELL_VISUAL_TYPE,
        update=update_paint,
    )
