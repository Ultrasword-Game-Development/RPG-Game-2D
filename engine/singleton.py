# ----------------------------------- #
# game settings

DEBUG = False
DEBUG_COLOR = (255, 0, 0)

# -------------------------------------------------- #
# window

WINDOW_WIDTH = 0
WINDOW_HEIGHT = 0

FB_WIDTH = 0
FB_HEIGHT = 0

FBWHALF = 0
FBHHALF = 0


# -------------------------------------------------- #
# chunks + world
TILEMAP_WIDTH = 8
TILEMAP_HEIGHT = 8
TILE_WIDTH = 18
TILE_HEIGHT = 18

CHUNK_PIX_WIDTH = TILE_WIDTH * TILEMAP_WIDTH
CHUNK_PIX_HEIGHT = TILE_HEIGHT * TILEMAP_HEIGHT


# -------------------------------------------------- #
# camera
WORLD_OFFSET_X = 0
WORLD_OFFSET_Y = 0

RENDER_DIS = [0, 0]

# -------------------------------------------------- #
# animation
HORIZONTAL_HITBOX_COL = (255, 0, 0)
VERTICAL_HITBOX_COL = (0, 0, 255)


# -------------------------------------------------- #
# particles
DEFAULT_WAIT_TIME = 1

PARTICLE_ID = 0
PARTICLE_X = 1          # x pos
PARTICLE_Y = 2          # y pos
PARTICLE_SXY = 3        # scale in x and y
PARTICLE_LIFE = 4       # lifetime
PARTICLE_MX = 5
PARTICLE_MY = 6

# -------------------------------------------------- #
# entities
ENTITY_HITBOX_COLOR = (255, 0, 0)
