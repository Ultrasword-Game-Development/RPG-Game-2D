from engine import maths

def rot_rect_90deg(rect, orect):
    """Rounds the rect to nearest orientation - counterclockwise"""
    result = pygame.Rect(0, 0, 0, 0)
    # newly rotate point
    result.x = rect.y
    result.y = orect.w-rect.right
    result.w = rect.h
    result.h = rect.w

    return result


import pygame



rect = pygame.Rect(1, 1, 2, 1)
orect = pygame.Rect(0, 0, 4, 4)
angle = 90

rect = rot_rect_90deg(rect, orect)
print(rect)
rect = rot_rect_90deg(rect, orect)
print(rect)
rect = rot_rect_90deg(rect, orect)
print(rect)
rect = rot_rect_90deg(rect, orect)
print(rect)


