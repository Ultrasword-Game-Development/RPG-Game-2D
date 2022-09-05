import math
import numpy as np

def __mod__(val, mod):
    if val < 0: return -(val%mod)
    return val%mod

def lerp(start, end, co):
    """Linear interpolation"""
    return (end-start)*co + start

def normalized_random():
    """Normalized Random"""
    return np.random.random() * 2 - 1.0

def rot_point_about(p: list, cp: list, angle: float):
    """Rotate a point about another point"""
    s, c = math.sin(angle), math.cos(angle)
    x, y = p[0] - cp[0], p[1] - cp[1]
    return [cp[0] + x*c - y*s, cp[1] + x*s + y*c]

def convert_array_to_int(arr):
    """Convert an array to integer array"""
    return list(map(int, arr))

def convert_rectxy_to_cartesian(point, area):
    """Convert he upside down pygame stuff to cartesian"""
    return [point[0], point[1]-area[1]]

