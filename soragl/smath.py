import math
import numpy as np
from pygame.math import Vector2

# ------------------------------------------------------------ #
# math functions
# ------------------------------------------------------------ #


def __mod__(val, mod):
    """Return the modulo of a and b"""
    return (val % mod) * np.sign(val)


def __clamp__(val, low, high):
    """Return value in range specified"""
    if val > high:
        return high
    if val < low:
        return low
    return val


# ------------------------------------------------------------ #
# curve functions
# ------------------------------------------------------------ #


class Curve:
    ZERO = 1 / 1e9
    INF = 1e9

    def value_at(self, x: float):
        """Return the value at x"""
        pass

    def above(self, point: tuple):
        """Return if the point above the given point"""
        return point.y > self.value_at(point.x)

    def below(self, point: tuple):
        """Return if the point below the given point"""
        return point.y < self.value_at(point.x)

    def distance_to(self, point: tuple):
        """Return the distance between the point and the curve"""
        return self.value_at(point.x) - point.y

    def distance_to_abs(self, point: tuple):
        """Return the abs distance between the point and the curve"""
        return abs(self.distance_to(point))

    # ------------------------------ #
    # stats

    def furthest_point(self, points: list):
        """Return the furthest point from the curve"""
        return max(points, key=lambda p: self.distance_to_abs(p))

    def closest_point(self, points: list):
        """Return the closest point from the curve"""
        return min(points, key=lambda p: self.distance_to_abs(p))

    def lowest_point(self, points: list):
        """Return the lowest point from the curve"""
        return min(points, key=lambda p: self.distance_to(p))

    def highest_point(self, points: list):
        """Return the highest point from the curve"""
        return max(points, key=lambda p: self.distance_to(p))


# ==== linear


class Linear(Curve):
    @classmethod
    def get_from_points(cls, p1: tuple, p2: tuple):
        """Return a Linear curve from two points"""
        dx = p2.x - p1.x
        if dx == 0:
            dx = Curve.ZERO
        m = (p2.y - p1.y) / dx
        b = p1.y - m * p1.x
        return cls(m, b)

    # ------------------------------ #

    def __init__(self, m: float, b: float):
        self.m = m
        self.b = b

    def value_at(self, x):
        """Return the value at x"""
        return self.m * x + self.b

    def intersect(self, other):
        """Find intersection coordinates with other linear line"""
        x = (self.b - other.b) / (other.m - self.m)
        return Vector2(x, self.value_at(x))

    def perpendicular_line(self, point: tuple):
        """Get the perpendicular line"""
        m = -1 / self.m
        b = point[1] + m * point[0]
        return Linear(m, b)
