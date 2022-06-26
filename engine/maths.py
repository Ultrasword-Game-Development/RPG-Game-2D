import math


def mod(num, div):
    """Modulus but not stupid python version where everything is pos"""
    if num < 0:
        return -(num % div)
    return num % div


def lerp(a, b, c):
    """Linear interpolation"""
    return (b - a) * c + a


def clamp(num, _min, _max):
    """Insert value, and make sure it stays between _min and _max"""
    if num < _min:
        return _min
    if num > _max:
        return _max
    return num


def collide_rect(r1, r2):
    """Test for a collision between two squares"""
    # if left greater than right
    # print(r1.pos, r2.pos)
    if r1.pos[0] > r2.pos[0] + r2.area[0]:
        return False
    # if right is less that left
    if r1.pos[0] + r1.area[0] < r2.pos[0]:
        return False
    # if top is greater than bottom
    if r1.pos[1] > r2.pos[1] + r2.area[1]:
        return False
    # if bottom is less than top
    if r1.pos[1] + r1.area[1] < r2.pos[1]:
        return False
    return True


def two_hash(left, right):
    """Hash 2 numbers"""
    return (left << 16) + right


def two_unhash(num):
    """Unhash a number into 2 numbers"""
    left = (num >> 16) + 1
    right = num - (left << 16)
    return left, right
