from numpy import uint8

from dataclasses import dataclass
from enum import IntEnum

class BladeState(IntEnum):
    OFF  = 0
    LOW  = 1
    HIGH = 2
    
class Blade:

    __slots__ = ('diameter', 'state')

    def __init__(self,diameter):
        self.diameter = diameter  # m
        self.state = BladeState.OFF

    # Lower blade darker grass!
    def cut(self):
        if self.state == BladeState.OFF:
            c = 0
        elif self.state == BladeState.LOW:
            c = 0.80 * 255
        elif self.state == BladeState.HIGH:
            c = 0.90 * 255
        return uint8(c)   

    def toggle(self):
        if self.state == BladeState.OFF:
            self.state = BladeState.LOW
        elif self.state == BladeState.LOW:
            self.state = BladeState.HIGH
        elif self.state == BladeState.HIGH:
            self.state = BladeState.OFF

    @staticmethod
    def color(state):
        if state == BladeState.OFF:
            c = None
        elif state == BladeState.LOW:
            c = (0.8, 0.8, 0.8)
        elif state == BladeState.HIGH:
            c = (0.9, 0.9, 0.9)
        return c
