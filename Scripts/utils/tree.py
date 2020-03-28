from random import shuffle


class Tree:
    tree_attr = 'tree'
    id = 0

    staticmethod

    def add(obj):
        if not hasattr(obj, Tree.tree_attr):
            setattr(obj, Tree.tree_attr, Tree())

    staticmethod

    def get(obj):
        try:
            return getattr(obj, Tree.tree_attr)
        except AttributeError:
            Tree.add(obj)
            return getattr(obj, Tree.tree_attr)

    staticmethod

    def can_merge(obj_a, obj_b):
        return obj_a and obj_b and not Tree.get(obj_a).is_connected_to(Tree.get(obj_b))    
        
    staticmethod

    def next_id():
        Tree.id += 1
        return Tree.id

    def __init__(self):
        self._parent = None
        self._childs = set()
        self.id = Tree.next_id()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Tree :' + self.name

    def _add_child(self, child_tree):
        self._childs.add(child_tree)

    def set_parent(self, parent_tree):
        if parent_tree is not self:
            self._parent = parent_tree
            parent_tree._add_child(self)

    def get_root(self):
        return self._parent.get_root() if self._parent else self

    def is_connected_to(self, other_tree):
        return self.get_root() == other_tree.get_root()

    def connect_to(self, other_tree):
        if not self.is_connected_to(other_tree):
            other_tree.get_root().set_parent(self)
