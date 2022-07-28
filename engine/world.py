import pygame
from . import globals, maths, chunk

class World:
    """
    World contains a dict of chunks
    Chunks are objects that contain:
    - tilemap
    - entities
    """
    def __init__(self):
        """
        Constructor for World
        contains:
        - chunks        = dict [str, list]
        """
        self.chunks = {}
    
    def add_chunk(self, chunk):
        """Adds a chunk to the world"""
        self.chunks[chunk.id] = chunk
    
    def get_chunk(self, x: int, y: int):
        """Get a chunk"""
        key = f"{x}-{y}"
        if key not in self.chunks:
            self.chunks[key] = chunk.Chunk(x, y)
        return self.chunks[key]
    
    def handle_chunks(self, surface):
        """Handles rendering of chunks"""
        # print("handling chunks")
        # TODO - create system for rendering chunks
        pass
    
    def move_entity(self, entity):
        """Move an entity through the chunk"""
        # find range of intercepting tiles
        intercept = pygame.Rect((entity.rect.x // globals.TILE_WIDTH - 1, entity.rect.y // globals.TILE_HEIGHT - 1), entity.tiles_area)
        # move x\
        entity.position.x += entity.motion.x
        # check for collisions with tilemap
        
        # move y
        entity.position.y += entity.motion.y
        # check for collisions with tilemap

        entity.chunk = (int(entity.position.x) // globals.CHUNK_PIX_WIDTH, int(entity.position.y) // globals.CHUNK_PIX_HEIGHT)
        if entity.chunk != entity.p_chunk:
            self.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).remove_entity(entity)
            entity.p_chunk = entity.chunk
            self.get_chunk(entity.chunk[0], entity.chunk[1]).add_entity(entity)
        # print(entity.name, entity.chunk)

    def find_nearby_entities(self, cpos: tuple, range: int):
        """Searches nearby chunks for entities - is an iterable"""
        for ix in range(cpos[0]-range, cpos[0]+range+1):
            for iy in range(cpos[1]-range, cpos[1]+range+1):
                c = self.get_chunk(ix, iy)
                if not c: continue
                for e in c.entities:
                    yield e



