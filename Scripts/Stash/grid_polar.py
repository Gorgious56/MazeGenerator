from os import path as os_path
from sys import path as sys_path
from random import choice, seed
import bpy
import importlib
from math import pi, floor, cos, sin
from mathutils import Vector

dir = os_path.dirname(bpy.data.filepath)+"\scripts"
if not dir in sys_path:
    sys_path.append(dir)    

import cell_polar
importlib.reload(cell_polar)
import grid
importlib.reload(grid)
CellPolar = cell_polar.CellPolar

class GridPolar(grid.Grid):
    def __init__(self, rows, columns, name="", cell_size=1):
        self.cell_size = max(0, cell_size)
        self.rows_polar = []
        super().__init__(rows, 1, name, 'polar', 4)        
    
    def prepare_grid(self):
        rows = [None] * self.rows
        row_height = 1 / self.rows
        rows[0] = [CellPolar(0,0)]
        
        for r in range(1, self.rows):
            radius = r / self.rows
            circumference = 2 * pi * radius
            
            previous_count = len(rows[r - 1])
            estimated_cell_width = circumference / previous_count
            ratio = round(estimated_cell_width / row_height + self.cell_size - 1)
            
            cells = previous_count * ratio
            rows[r] = [CellPolar(r, col) for col in range(cells)]
        self.rows_polar = rows
        
        
    def __delitem__(self, key):
        del self[key[0], key[1]]
    def __getitem__(self, key):
        try:
            return self.rows_polar[key[0]][key[1]] 
        except Exception as e:
#            print(type(e))
            return None
    def __setitem__(self, key, value):
        try:
            self.rows_polar[key[0]][key[1]] = value
        except:
            pass   
        
    def each_row(self):
        for r in self.rows_polar:
            yield r   
        
    def each_cell(self):
        for r in self.each_row():
            for c in r:
                if c and not c.is_masked:
                    yield c
                
    def get_unmasked_cells(self): # Legacy.
        return [c for c in self.each_cell()]
                
    def random_cell(self, _seed = None, filter_mask=True):
        if _seed:
            seed(_seed)
        return choice([c for c in choice(self.rows_polar) if not c.is_masked])

    def configure_cells(self):        
        for c in self.each_cell():
            row, col = c.row, c.column
            if row > 0:
                c.ccw = self[row, col - 1]
                c.cw = self[row, (col + 1) % len(self.rows_polar[row])]

                ratio = len(self.rows_polar[row]) / len(self.rows_polar[row - 1])
                parent = self[row - 1, floor(col // ratio)]
                parent.outward.append(c)
                
                c.inward = parent
    
    def get_cell_position(self, c, row_length, cell_size, offset):
        t = 2 * pi / row_length
        r_in = (c.row ) * cell_size
        r_out = (c.row + 1) * cell_size
        t_cw = (c.column + 1) * t
        t_ccw = c.column * t
        
        ax = r_in * cos(t_ccw)
        ay = r_in * sin(t_ccw)
        bx = r_out * cos(t_ccw)
        by = r_out * sin(t_ccw)
        cx = r_in * cos(t_cw)
        cy = r_in * sin(t_cw)
        dx = r_out * cos(t_cw)
        dy = r_out * sin(t_cw)
        
        A = Vector([ax, ay, 0]) - offset
        B = Vector([bx, by, 0]) - offset
        C = Vector([cx, cy, 0]) - offset
        D = Vector([dx, dy, 0]) - offset
        
        center = (A + B + C + D) / 4
          
        return center, C, D, B, A