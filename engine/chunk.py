import pygame

from .globals import *
from . import tile


class Chunk:
    def __init__(self, x, y):
        """
        Constructor for Chunk
        contains:
        - area_rect         = pygame.Rect
        - world_chunk_tile  = [int, int]
        - world_rel_pos     = [float, float]
        - tilemap           = [Tile...etc]
        - environment       = [static_entity...etc]
        - id                = str

        Tiles can be updated externally via custom made entities
        - some premade entities include AnimatedTiles etc
        
        Tiles can be modified by getting then changing specific params
        - new tiles cannot be set
        """
        self.id = f"{x}-{y}"
        self.world_chunk_tile = (x,y)
        self.world_rel_pos = (x * TILE_WIDTH * TILEMAP_WIDTH, y * TILE_HEIGHT * TILEMAP_HEIGHT)
        self.area_rect = pygame.Rect(self.world_rel_pos, (TILE_WIDTH * TILEMAP_WIDTH, TILE_HEIGHT * TILEMAP_HEIGHT))
        self.tilemap = tuple(tuple(tile.Tile(x,y,self) for x in range(TILEMAP_WIDTH)) for y in range(TILEMAP_HEIGHT))
        self.environment = []
    
    def get_tile_at(self, x, y):
        """Get a tile"""
        return self.tilemap[y][x]
    
    def render(self, surface):
        """Render function"""
        for y in range(TILEMAP_HEIGHT):
            for x in range(TILEMAP_WIDTH):
                if self.tilemap[y][x].visible and self.tilemap[y][x].sprite:
                    surface.blit(self.tilemap[y][x].sprite, self.tilemap[y][x].world_hitbox)