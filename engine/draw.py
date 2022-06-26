import pygame


EMPTY_ALPHA = pygame.SRCALPHA


DEBUG_DRAW_LINES = pygame.draw.lines
DEBUG_DRAW_LINE = pygame.draw.line

DRAW_RECT = pygame.draw.rect
DRAW_CIRCLE = pygame.draw.circle
DRAW_ANTI_ALIAS_LINE = pygame.draw.aaline
DRAW_ARC = pygame.draw.arc

def DEBUG_DRAW_RECT(surface, rect, offset=(0,0)):
    """Debug draw a rect"""
    DEBUG_DRAW_LINES(surface, (255, 0, 0), True, (
        (rect.x + offset[0], rect.y + offset[1]), (rect.right + offset[0], rect.y + offset[1]), 
        (rect.right + offset[0], rect.bottom + offset[1]), (rect.x + offset[0], rect.bottom + offset[1])))