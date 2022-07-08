import math
import numpy as np

def lerp(start, end, co):
    """Linear interpolation"""
    return (end-start)*co + start



def normalized_random():
    """Normalized Random"""
    return np.random.random() * 2 - 1.0


