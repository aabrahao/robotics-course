from dataclasses import dataclass
from enum import IntEnum

class BladeState(IntEnum):
    OFF  = 0
    LOW  = 1
    HIGH = 2
    
@dataclass
class Blade:

    diameter : float = 0.0 # m
    state : BladeState = BladeState.OFF

    # Lower blade darker grass!
    def cut(self):
        if self.state == BladeState.OFF:
            return None
        elif self.state == BladeState.LOW:
            return 0.80*255
        elif self.state == BladeState.HIGH:
            return 0.90*255   

    def toggle(self):
        if self.state == BladeState.OFF:
            self.state = BladeState.LOW
        elif self.state == BladeState.LOW:
            self.state = BladeState.HIGH
        elif self.state == BladeState.HIGH:
            self.state = BladeState.OFF   
