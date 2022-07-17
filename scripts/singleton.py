import pygame

# ----------- WORLD -------------- #

GRAVITY = 80
UP = pygame.math.Vector2(0,-1)
RIGHT = pygame.math.Vector2(1,0)
DOWN = pygame.math.Vector2(0,1)
LEFT = pygame.math.Vector2(-1,0)

# ---------- Singletons ----------- #

PLAYER = None
