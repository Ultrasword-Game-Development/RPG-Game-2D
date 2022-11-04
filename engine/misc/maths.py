import math
import numpy as np

from typing import List, Union, Tuple, Any

INT_OR_FLOAT = Union[int, float]


def __mod__(val: INT_OR_FLOAT, mod: INT_OR_FLOAT) -> INT_OR_FLOAT:
    """Mod but better"""
    if val < 0: return -(val % mod)
    return val % mod


def lerp(start: Any, end: Any, co: INT_OR_FLOAT) -> Any:
    """Linear interpolation"""
    return (end - start) * co + start


def normalized_random() -> float:
    """Normalized Random"""
    return np.random.random() * 2 - 1.0


def rot_point_about(p: list, cp: list, angle: float) -> List[INT_OR_FLOAT]:
    """Rotate a point about another point"""
    s, c = math.sin(angle), math.cos(angle)
    x, y = p[0] - cp[0], p[1] - cp[1]
    return [p[0] + x * c - y * s, cp[1] + x * s + y * c]


def convert_array_to_int(arr: List[INT_OR_FLOAT]) -> List[INT_OR_FLOAT]:
    """Convert an array to integer array"""
    return list(map(int, arr))


def convert_rectxy_to_cartesian(point: List[INT_OR_FLOAT], area: List[INT_OR_FLOAT]) -> List[INT_OR_FLOAT]:
    """Convert he upside down pygame stuff to cartesian"""
    return [point[0], point[1] - area[1]]


def hex_to_tuple(hex: str) -> List[INT_OR_FLOAT]:
    """Convert hex to tuple (rgb)"""
    return [int(hex[i * 2:i * 2 + 2], base=16) for i in range(3)]
