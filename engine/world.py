import pygame
from . import globals


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
        self.entities = set()
    
    def add_chunk(self, chunk):
        """Adds a chunk to the world"""
        self.chunks[chunk.id] = chunk
    
    def get_chunk(self, x: int, y: int):
        """Get a chunk"""
        return self.chunks.get(f"{x}-{y}")
    
    def handle_chunks(self, surface):
        """Handles rendering of chunks"""
        # print("handling chunks")
        # TODO - create system for rendering chunks
        pass
    
    def move_entity(self, entity):
        """Move an entity through the chunk"""
        # find range of intercepting tiles
        intercept = pygame.Rect((entity.rect.x // globals.TILE_WIDTH - 1, entity.rect.y // globals.TILE_HEIGHT - 1), entity.tiles_area)
        # move x
        entity.position.x += entity.motion.x
        
        # move y
        entity.position.y += entity.motion.y


