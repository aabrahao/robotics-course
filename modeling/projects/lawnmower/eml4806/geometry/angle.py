import numpy as np

def wrap(radians):
    ''' Normalize angle to the range [-pi, pi) '''
    return (radians + np.pi) % (2 * np.pi) - np.pi