"""
Contains definitions and methods to store and access Collections
"""


import bpy
from typing import List


class CollectionsPropertyGroup(bpy.types.PropertyGroup):
    """
    Stores the collections used in the add-on
    """
    objects: bpy.props.PointerProperty(
        name="Collection storing the add-on's objects",
        type=bpy.types.Collection)


def link_objects_to_collection(
        objects: List[bpy.types.Object],
        new_col: bpy.types.Collection,
        unlink_from_existing: bool = True) -> None:
    for obj in (obj for obj in objects if obj):
        if unlink_from_existing:
            for col in obj.users_collection:
                col.objects.unlink(obj)
        if obj.name not in new_col.objects:
            new_col.objects.link(obj)
