"""
Contains definitions and methods to store and access Collections
"""


from typing import Iterable
from bpy.types import Object, Collection


def link_objects_to_collection(
    objects: Iterable[Object], new_col: Collection, unlink_from_existing: bool = True
) -> None:
    for obj in (obj for obj in objects if obj):
        if unlink_from_existing:
            for col in obj.users_collection:
                col.objects.unlink(obj)
        if obj.name not in new_col.objects:
            new_col.objects.link(obj)
