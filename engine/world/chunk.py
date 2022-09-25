import pygame

from .. singleton import *


class Chunk:
    def __init__(self, x, y, world):
        """
        Constructor for Chunk
        contains:
        - area_rect         = pygame.Rect
        - world_chunk_tile  = [int, int]
        - world_rel_pos     = [float, float]
        - tilemap           = [Tile...etc]
        - environment       = [static_entity...etc]
        - id                = str

        Tiles can be updated externally via custom-made entities
        - some premade entities include AnimatedTiles etc
        
        Tiles can be modified by getting then changing specific params
        - new tiles cannot be set
        """
        self.id = f"{x}-{y}"
        self.world_chunk_tile = (x,y)
        self.world_rel_pos = (x * TILE_WIDTH * TILEMAP_WIDTH, y * TILE_HEIGHT * TILEMAP_HEIGHT)
        self.area_rect = pygame.Rect(self.world_rel_pos, (TILE_WIDTH * TILEMAP_WIDTH, TILE_HEIGHT * TILEMAP_HEIGHT))
        # -------------------------------------------------- #
        # environment objects
        self.env = set()
        self.entities = set()
        self.world = world

    def handle(self, surface):
        """Handle all objects within the chunk"""
        # update entities in the chunk
        for e in self.env:
            self.world.env.entity_buffer[e].update()
            # check if entities are to be removed
            if e not in self.world.env.to_remove:
                self.world.env.entity_buffer[e].render(surface)
        # that is all :)

    def debug_handle(self, surface):
        """Debug handle all objects within the chunk"""
        # update entities
        for e in self.env:
            self.world.env.entity_buffer[e].update()
            # check if entiites are to be removed
            if e not in self.world.env.to_remove:
                self.world.env.entity_buffer[e].render(surface)
                self.world.env.entity_buffer[e].debug(surface)

    def add_env_obj(self, obj):
        """Environment object"""
        self.env.add(obj.id)

    def remove_env_obj(self, obj):
        """Remove and obj"""
        if obj.id in self.env:
            self.env.remove(obj.id)

    def add_entity(self, entity):
        """Add an entity to this chunk"""
        self.entities.add(entity.id)
    
    def remove_entity(self, entity):
        """Remove an entity"""
        if entity.id in self.entities:
            self.entities.remove(entity.id)


