# chunks will have a set size of 12 x 12
CHUNK_WIDTH = CHUNK_HEIGHT = 12
CHUNK_TILE_WIDTH = CHUNK_TILE_HEIGHT = 64
CHUNK_WIDTH_PIX = CHUNK_WIDTH * CHUNK_TILE_WIDTH
CHUNK_HEIGHT_PIX = CHUNK_HEIGHT * CHUNK_TILE_HEIGHT
CHUNK_TILE_AREA = (CHUNK_TILE_WIDTH, CHUNK_TILE_HEIGHT)

TILE_X = 0
TILE_Y = 1
TILE_IMG = 2
TILE_COL = 3



"""
Basically, each object has a serialize and deserialize method

World and Handler was serialize_world and serialize_handler respectively for both
serialization and deserialization

"""

# serialization
PICKLE_DUMP_PROTOCOL = 4

CHUNK_TILEMAP_KEY = "tile"
CHUNK_POS_KEY = "pos"

ANIMATION_PATH_KEY = "a_path"
ANIMATION_NAME_KEY = "a_name"
ANIMATION_ISSPRITESHEET_KEY = "a_spritesheet?"

RECT_X_KEY = "x"
RECT_Y_KEY = "y"
RECT_W_KEY = "w"
RECT_H_KEY = "h"

TILE_DATA_FRICTION_KEY = "friction"
# TBD
TILE_DATA_OTHER_JKEY = "other"

TILE_X_KEY = "x"
TILE_Y_KEY = "y"
TILE_IMG_KEY = "img"
TILE_COL_KEY = "col"
TILE_STATS_KEY = "stats"
TILE_TYPE_KEY = "type"
TILE_EXTRA_DATA_KEY = "extra"

ENTITY_RECT_KEY = "rect"
ENTITY_ANIMATION_KEY = "animation"
ENTITY_TYPE_KEY = "type"
ENTITY_DATA_KEY = "data"
ENTITY_STRING_IDENTIFIER_KEY = "identifier"

SPRITETILE_INDEX_KEY = "index"
SPRITETILE_RECT_KEY = "rect"
SPRITETILE_PARENT_IMAGE_KEY = "parent_str"

SPRITESHEET_IMAGE_PATH_KEY = "s_path"
SPRITESHEET_SPRITES_KEY = "s_tiles"
SPRITESHEET_SPRITE_AREA_KEY = "s_area"
SPRITESHEET_SPACING_KEY = "s_spacing"

HANDLER_ENTITIES_KEY = "entities"
HANDLER_ENTITY_TYPES_KEY = "etypes"

WORLD_CHUNK_KEY = "chunks"
WORLD_RENDER_DISTANCE_KEY = "r_dist"
WORLD_GRAVITY_KEY = "gravity"
WORLD_TILE_TYPES = "tiletypes"

STATE_HANDLER_KEY = "handler"
STATE_WORLD_KEY = "world"


# world rendering

SPRITE_OBJECT_PREFIX = "spr_o_"

SPRITE_OBJECT_KEY = "sprite"
SPRITE_OBJECT_IMG_KEY = "img"

# sprite sheet stuffs

SPRITETILE_SHEET_KEY = "sheet"
SPRITETILE_SHEET_INDEX_KEY = "index"
SPRITETILE_SHEET_DATA_KEY = "data"


"""
Registered Object Names
"""

REG_OBJECT_KEY = "object"
REG_P_OBJECT_KEY = "p_object"
