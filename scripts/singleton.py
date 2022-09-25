import pygame

# -------------------------------------------------- #
# world

GRAVITY = 80
UP = pygame.math.Vector2(0,-1)
RIGHT = pygame.math.Vector2(1,0)
DOWN = pygame.math.Vector2(0,1)
LEFT = pygame.math.Vector2(-1,0)

ZERO = pygame.math.Vector2(0,0)

# -------------------------------------------------- #
# const value

HANDLE_IDENTIFIER = "handler"
HANDLE_POS_COL = (0, 255, 0)

# -------------------------------------------------- #
# singletons

PLAYER = None

# -------------------------------------------------- #
# event + function wrappers
ATTACK_PARTICLE_CREATE_ID = "attack-create"
ATTACK_PARTICLE_CREATE = None

# -------------------------------------------------- #
#

