import pygame

# ----------- WORLD -------------- #

GRAVITY = 80
UP = pygame.math.Vector2(0,-1)
RIGHT = pygame.math.Vector2(1,0)
DOWN = pygame.math.Vector2(0,1)
LEFT = pygame.math.Vector2(-1,0)

# ---------- const values  ---------------- #

HANDLE_IDENTIFIER = "handler"
HANDLE_POS_COL = (0, 255, 0)

# ---------- Singletons ----------- #

PLAYER = None


