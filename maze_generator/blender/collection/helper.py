"""
Contains definitions and methods to store and access Collections
"""

import bpy
from typing import Iterable


def link_objects_to_collection(
    objects: Iterable[bpy.types.Object], new_col: bpy.types.Collection, unlink_from_existing: bool = True
) -> None:
    for obj in (obj for obj in objects if obj):
        if unlink_from_existing:
            for col in obj.users_collection:
                col.objects.unlink(obj)
        if obj.name not in new_col.objects:
            new_col.objects.link(obj)


def get_or_create_collection(scene: bpy.types.Scene, name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
    if col.name not in scene.collection.children:
        scene.collection.children.link(col)
    return col
