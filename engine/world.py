"""
world.py

Chunks:
- chunk_id
- position (x, y)
- world_pos (x, y)
- image_cache: map of images
- tile_map: ALL THE TILES- THE GLORY IS REAL

World:
- chunks: map of chunks
- r_distance: render distance

What an amazing file; we have so much cool stuff!


"""


import pygame
import pickle
from engine import filehandler, window
from engine.globals import *

from dataclasses import dataclass


# TODO - tile object type thing

TILE_TYPE_ACCESS_CONTAINER = {}

def register_tile_type(name: str, tile_type: type):
    """Registers the object type"""
    TILE_TYPE_ACCESS_CONTAINER[name] = (tile_type, name)



# ---------------- tile data ----------------

@dataclass(init=False)
class TileData:
    """
    Tile data object
    - stores stats
    
    data:
    - friction
    - ...
    """

    friction: float

    def __init__(self, friction: float):
        """TileData constructor"""
        self.friction = friction
    
    def serialize(self) -> dict:
        """Serialize this tile data object"""
        return {TILE_DATA_FRICTION_KEY: self.friction}

    @staticmethod
    def deserialize(data):
        """Deserialize the data"""
        if not data:
            return False
        result = TileData(float(data[TILE_DATA_FRICTION_KEY]))
        
        return result

# ------------------ tile --------------------- #

@dataclass(init=False)
class Tile:
    """
    Tile object
    - stores what tiles store ;-;

    x and y are relative to the chunk:
    - are the x and y index in the chunk.tile_map[y][x]
    """

    x: int
    y: int
    img: str
    collide: int
    tilestats: TileData

    # this is important for sprite tiles
    data: dict
    
    # class variable
    tile_type: str = "tile"

    def __init__(self, x: int, y: int, img: str, collide: int, data: TileData = None):
        """Tile constructor"""
        self.x = x
        self.y = y
        self.img = img
        self.collide = collide
        self.tilestats = data
        self.data = {}

    def render(self, surface, images: dict, offset: tuple = (0, 0)) -> None:
        """Render function for this tile"""
        # I have no idea if this will be slower
        # i don't know how python function stack works 
        # if has intelligence on this topic, please inform me :D
        if self.img:
            surface.blit(images[self.img], (self.x + offset[0], self.y + offset[1]))
    
    def cache_image(self, cache) -> None:
        """Cache the image"""
        if not self.img:
            return
        if not cache.get(self.img):
            cache[self.img] = filehandler.scale(filehandler.get_image(self.img), CHUNK_TILE_AREA)

    @property
    def stats(self):
        """Get stats"""
        return self.tilestats
    
    @stats.setter
    def stats(self, other):
        """Set Stats"""
        self.tilestats = other

    def serialize(self, parent_pos: tuple) -> dict:
        """Serialize this tile"""
        result = {}
        result[TILE_X_KEY] = (self.x - parent_pos[0]) // CHUNK_TILE_WIDTH
        result[TILE_Y_KEY] = (self.y - parent_pos[1]) // CHUNK_TILE_HEIGHT
        result[TILE_IMG_KEY] = self.img
        result[TILE_COL_KEY] = self.collide
        if self.tilestats:
            result[TILE_STATS_KEY] = self.tilestats.serialize()
        else:
            result[TILE_STATS_KEY] = None
        result[TILE_TYPE_KEY] = self.tile_type
        result[TILE_EXTRA_DATA_KEY] = self.data
        # add img
        # graphics[GRAPHICS_IMAGE_KEY].add(self.img)
        return result
    
    @staticmethod
    def deserialize(data):
        """Deserialize a data block"""
        # get the type
        tile_name = data[TILE_TYPE_KEY]
        tile_type = TILE_TYPE_ACCESS_CONTAINER[tile_name][0]
        if tile_name == Tile.tile_type:
            return tile_type(int(data[TILE_X_KEY]), int(data[TILE_Y_KEY]), data[TILE_IMG_KEY], data[TILE_COL_KEY], TileData.deserialize(data[TILE_STATS_KEY]))
        else:
            return tile_type.deserialize(data)

# ---------- chunk ------------ #

class Chunk:
    def __init__(self, pos: tuple):
        """Chunk Constructor"""
        self.chunk_id = pos[0] + (pos[1] << 16)
        self.pos = (pos[0], pos[1])
        self.world_pos = (pos[0] * CHUNK_WIDTH_PIX, pos[1] * CHUNK_HEIGHT_PIX)

        # images are all references cuz python only uses refs
        self.images = {}

        # visual aspects
        self.tile_map = [[Chunk.create_grid_tile(x, y, None) for x in range(CHUNK_WIDTH)] for y in range(CHUNK_HEIGHT)]

    @property
    def id(self) -> int:
        """get the chunk id pos"""
        return self.chunk_id
    
    @staticmethod
    def create_grid_tile(x: int, y: int, img: str, collide: int = 0, data: TileData = None):
        """
        Create a tile object
        
        The position from (x, y) is converted to 
                (x * TILE_WIDTH + self.world_pos[0], y * TILE_HEIGHT + self.world_pos[1])
        
        This ensures unecassary calculations are not performed
        """
        # return [x, y, img, collide]
        return Tile(x, y, img, collide, data=data)

    def set_tile_at(self, tile) -> None:
        """Set a tile at - get the tile data from Chunk.create_grid_tile()"""
        tile.cache_image(self.images)
        # get the object in cache
        self.tile_map[tile.y][tile.x] = tile
        tile.x = tile.x * CHUNK_TILE_WIDTH + self.world_pos[0]
        tile.y = tile.y * CHUNK_TILE_HEIGHT + self.world_pos[1]

    def render(self, offset: tuple = (0, 0)) -> None:
        """Renders all the grid tiles and non tile objects"""
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                # get block data
                self.tile_map[y][x].render(window.FRAMEBUFFER, self.images, offset=offset)

    def is_collide(self, x: int, y: int, rect) -> bool:
        """Check if a block is collided with the chunk block"""
        block = self.tile_map[y][x]
        if not block.collide:
            return block.collide
        if block.x > rect.right:
            return False
        if block.y > rect.bottom:
            return False
        if block.x + CHUNK_TILE_WIDTH < rect.left:
            return False
        if block.y + CHUNK_TILE_HEIGHT < rect.top:
            return False
        return True

    def serialize(self) -> dict:
        """
        Serialize chunk
        
        Only two parts, the tiles and the position
        - images are stored in graphics
        - iterate through each tile and call serialize method
        - then ez dubs
        """
        result = {}
        result[CHUNK_TILEMAP_KEY] = []
        for y in range(CHUNK_HEIGHT):
            result[CHUNK_TILEMAP_KEY].append([])
            for x in range(CHUNK_WIDTH):
                result[CHUNK_TILEMAP_KEY][y].append(self.tile_map[y][x].serialize(self.world_pos))
        result[CHUNK_POS_KEY] = list(self.pos)

        return result
    
    @staticmethod
    def deserialize(data: dict):
        """
        Deserialize the Chunk object

        - take in dict
        - decode to get the 
            - tiles
            - position
        """
        position = data[CHUNK_POS_KEY]
        tile_data = data[CHUNK_TILEMAP_KEY]

        result = Chunk(position)
        for y in range(CHUNK_HEIGHT):
            for x in range(CHUNK_WIDTH):
                # get tile and deserialize
                tile = Tile.deserialize(tile_data[y][x])
                # set tile
                result.set_tile_at(tile)
        
        return result


# -------------- world ---------------- #

class World:
    def __init__(self):
        """World Constructor"""
        self.chunks = {}
        
        # args
        self.r_distance = 2

        # physics data
        self.gravity = 90
        
    def add_chunk(self, chunk: Chunk) -> None:
        """add a chunk to the world"""
        self.chunks[chunk.chunk_id] = chunk
    
    def make_template_chunk(self, x: int, y: int) -> Chunk:
        """Make a default empty chunk"""
        self.chunks[x + (y << 16)] = Chunk((x, y))
        return self.get_chunk(x, y)
    
    def get_chunk(self, x: int, y: int) -> Chunk:
        """Get chunk from the world chunk cache"""
        return self.chunks.get(x + (y << 16))
    
    def render_chunks(self, rel_center: tuple, offset: tuple = (0, 0)) -> None:
        """Render the world with the set render distance | include a center"""
        for cx in range(rel_center[0] - self.render_distance, rel_center[0] + self.render_distance + 1):
            for cy in range(rel_center[1] - self.render_distance, rel_center[1] + self.render_distance + 1):
                if self.get_chunk(cx, cy):
                    self.get_chunk(cx, cy).render(offset)
    
    @property
    def render_distance(self) -> int:
        """Return render distance"""
        return self.r_distance
    
    @render_distance.setter
    def render_distance(self, new: int) -> int:
        """Set render distance"""
        self.r_distance = new

    # --------------- serialize + deserialize ------------ #

    def serialize_world(self) -> dict:
        """
        Deserialize World

        Takes each chunk and serializes the chunk
        - store chunk data into an array
        - chunks should also store the required graphics
        """
        
        result = {}
        
        # serialize chunks
        result[WORLD_CHUNK_KEY] = []
        for chunk_id, chunk in self.chunks.items():
            result[WORLD_CHUNK_KEY].append(chunk.serialize())
        
        # serialize render distance and gravity
        result[WORLD_RENDER_DISTANCE_KEY] = self.r_distance
        result[WORLD_GRAVITY_KEY] = self.gravity

        # save all tile types as well
        tt = {}
        for tile_name, tile_data in TILE_TYPE_ACCESS_CONTAINER.items():
            tt[tile_name] = pickle.dumps(TILE_TYPE_ACCESS_CONTAINER[tile_name], protocol=PICKLE_DUMP_PROTOCOL).hex()
        result[WORLD_TILE_TYPES] = tt

        return result
    
    @staticmethod
    def deserialize_world(data: dict):
        """
        Deserialize world

        Take the given data and creates a world object
        """
        result = World()
        # deserialize render distance and gravity
        result.r_distance = data[WORLD_RENDER_DISTANCE_KEY]
        result.gravity = data[WORLD_GRAVITY_KEY]
        # load all tile types
        for tile_name, encoded_bytes in data[WORLD_TILE_TYPES].items():
            # decode the data - to a tuple
            decoded = bytes.fromhex(encoded_bytes)
            unpickled = pickle.loads(decoded)
            # add to the global object type access container
            TILE_TYPE_ACCESS_CONTAINER[tile_name] = unpickled

        # deserialize world data / chunks
        for chunk in data[WORLD_CHUNK_KEY]:
            result.add_chunk(Chunk.deserialize(chunk))
        
        return result

    # --------------- physics part ----------- #
    def move_object(self, object) -> None:
        """
        Move an object using AABB object
        
        - should be importing state.py
        - then calling state.CURRENT.move_object(self)
        - usually called within the object
        """
        object.m_moving[0] = False
        object.m_moving[1] = False
        p_motion = [round(object.p_motion[0]), round(object.p_motion[1])]
        pos = object.rect.pos
        area = object.rect.area
        motion = (round(object.m_motion[0]), round(object.m_motion[1]))

        if p_motion[0] != motion[0]:
            object.m_moving[0] = True
        if p_motion[1] != motion[1]:
            object.m_moving[1] = True

        object.p_motion[0] = object.m_motion[0]
        object.p_motion[1] = object.m_motion[1]

        c_area = (area[0] // CHUNK_WIDTH_PIX + 1, area[1] // CHUNK_HEIGHT_PIX + 1)
        t_rect = (object.rect.cx, object.rect.cy, object.rect.w // CHUNK_TILE_WIDTH, object.rect.h // CHUNK_TILE_HEIGHT)

        # loop through each chunk
        chunks = []
        for x in range(object.rect.cx - c_area[0], object.rect.cx + c_area[0] + 1):
            for y in range(object.rect.cy - c_area[1], object.rect.cy + c_area[1] + 1):
                if self.get_chunk(x, y):
                    chunks.append(self.get_chunk(x, y))
                
        # print(chunks)

        # move x
        object.rect.x += motion[0]
        for chunk in chunks:
            # TODO - implement collision handling
            for xi in range(CHUNK_WIDTH):
                for yi in range(CHUNK_HEIGHT):
                    # check if collide
                    if not chunk.is_collide(xi, yi, object.rect):
                        continue
                    # check for motion
                    if motion[0] > 0:
                        # moving right
                        object.rect.x = chunk.tile_map[yi][xi].x - object.rect.w - 0.1
                        object.m_motion[0] = 0
                    elif motion[0] < 0:
                        # moving left
                        object.rect.x = chunk.tile_map[yi][xi].x + CHUNK_TILE_WIDTH + 0.1
                        object.m_motion[0] = 0

        # move y
        object.rect.y += motion[1]
        for chunk in chunks:
            # check
            for xi in range(CHUNK_WIDTH):
                for yi in range(CHUNK_HEIGHT):
                    # check if collide
                    if not chunk.is_collide(xi, yi, object.rect):
                        continue
                    # check for motion
                    if motion[1] > 0:
                        # moving right
                        object.rect.y = chunk.tile_map[yi][xi].y - object.rect.h - 0.1
                        object.m_motion[1] = 0
                    elif motion[1] < 0:
                        # moving left
                        object.rect.y = chunk.tile_map[yi][xi].y + CHUNK_TILE_HEIGHT + 0.1
                        object.m_motion[1] = 0    

        # set object chunk position
        object.rect.cx = int(object.rect.x // CHUNK_WIDTH_PIX)
        object.rect.cy = int(object.rect.y // CHUNK_HEIGHT_PIX)


# ------- register the tile type ---------- #
register_tile_type(Tile.tile_type, Tile)

