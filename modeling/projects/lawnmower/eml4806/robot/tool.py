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
