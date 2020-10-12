"""
Module to auto-import packages recursively from the root directory.
Add a __init__.py file in any subfolder to automatically register classes.
"""

import typing
import inspect
import pkgutil
import importlib
from pathlib import Path
import bpy


class AutoLoad:
    """
    AutLoad standard class
    Create a new instance to initialize modules
    Call register() and unregister() when needed
    """

    def __init__(self):
        self.modules = self.get_all_submodules(Path(__file__).parent)
        self.ordered_classes = self.get_ordered_classes_to_register(
            self.modules)

    def register(self):
        for cls in self.ordered_classes:
            try:
                bpy.utils.register_class(cls)
            except ValueError:
                pass

        for module in self.modules:
            if module.__name__ == __name__:
                continue
            if hasattr(module, "register"):
                module.register()

    def unregister(self):
        for cls in reversed(self.ordered_classes):
            bpy.utils.unregister_class(cls)

        for module in self.modules:
            if module.__name__ == __name__:
                continue
            if hasattr(module, "unregister"):
                module.unregister()

    # Import modules
    #################################################

    @staticmethod
    def get_all_submodules(directory):
        return list(AutoLoad.iter_submodules(directory, directory.name))

    @staticmethod
    def iter_submodules(path, package_name):
        for name in sorted(AutoLoad.iter_submodule_names(path)):
            yield importlib.import_module("." + name, package_name)

    @staticmethod
    def iter_submodule_names(path, root=""):
        for _, module_name, is_package in pkgutil.walk_packages((str(path),)):
            if is_package:
                sub_path = path / module_name
                sub_root = root + module_name + "."
                yield from AutoLoad.iter_submodule_names(sub_path, sub_root)
            else:
                yield root + module_name

    # Find classes to register
    #################################################

    @staticmethod
    def get_ordered_classes_to_register(modules):
        return AutoLoad.toposort(AutoLoad.get_register_deps_dict(modules))

    @staticmethod
    def get_register_deps_dict(modules):
        deps_dict = {}
        classes_to_register = set(AutoLoad.iter_classes_to_register(modules))
        for cls in classes_to_register:
            deps_dict[cls] = set(
                AutoLoad.iter_own_register_deps(cls, classes_to_register))
        return deps_dict

    @staticmethod
    def iter_own_register_deps(cls, own_classes):
        yield from (dep for dep in AutoLoad.iter_register_deps(cls) if dep in own_classes)

    @staticmethod
    def iter_register_deps(cls):
        for value in typing.get_type_hints(cls, {}, {}).values():
            dependency = AutoLoad.get_dependency_from_annotation(value)
            if dependency is not None:
                yield dependency

    @staticmethod
    def get_dependency_from_annotation(value):
        if isinstance(value, tuple) and len(value) == 2:
            if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                return value[1]["type"]
        return None

    @staticmethod
    def iter_classes_to_register(modules):
        base_types = AutoLoad.get_register_base_types()
        for cls in AutoLoad.get_classes_in_modules(modules):
            if any(base in base_types for base in cls.__bases__):
                if not getattr(cls, "is_registered", False):
                    yield cls

    @staticmethod
    def get_classes_in_modules(modules):
        classes = set()
        for module in modules:
            for cls in AutoLoad.iter_classes_in_module(module):
                classes.add(cls)
        return classes

    @staticmethod
    def iter_classes_in_module(module):
        for value in module.__dict__.values():
            if inspect.isclass(value):
                yield value

    @staticmethod
    def get_register_base_types():
        return set(getattr(bpy.types, name) for name in [
            "Panel", "Operator", "PropertyGroup",
            "AddonPreferences", "Header", "Menu",
            "Node", "NodeSocket", "NodeTree",
            "UIList", "RenderEngine"
        ])

    # Find order to register to solve dependencies
    #################################################

    @staticmethod
    def toposort(deps_dict):
        sorted_list = []
        sorted_values = set()
        while len(deps_dict) > 0:
            unsorted = []
            for value, deps in deps_dict.items():
                if len(deps) == 0:
                    sorted_list.append(value)
                    sorted_values.add(value)
                else:
                    unsorted.append(value)
            deps_dict = {value: deps_dict[value] -
                         sorted_values for value in unsorted}
        return sorted_list
