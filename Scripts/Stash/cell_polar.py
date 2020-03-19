from os import path as os_path
from sys import path as sys_path
import bpy
import importlib
import cell

class CellPolar(cell.Cell):
    def __init__(self, row, column):
        super().__init__(row, column)
        self.cw = None
        self.ccw = None
        self.inward = None
        self.outward = []
        
    def get_neighbors(self):
        neighbors = []
        if self.cw :
            neighbors.append(self.cw)
        if self.ccw:
            neighbors.append(self.ccw)
        if self.inward:
            neighbors.append(self.inward)
        neighbors.extend(self.outward)
        return neighbors