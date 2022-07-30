import pygame

from dataclasses import dataclass

from .singleton import *
from .filehandler import Filehandler

def calculate_world_position(tchunk_pos, cworld_pos):
    return (TILE_WIDTH * (tchunk_pos[0] + cworld_pos[0] * TILEMAP_WIDTH), TILE_HEIGHT * (tchunk_pos[1] + cworld_pos[1] * TILEMAP_HEIGHT))

def handle_collision(self, entity):
    """
    Handles a collision with an entity
    1. world detects a collision with the world_hitbox
    2. tile handles the collision
    """
    pass


class Tile:
    """
    Tile Dataclass Object
    - holds simple data
    """
    def __init__(self, x, y, parent):
        """
        Constructor for Tile
        contains:
        - position      = (int, int)
        - world_hitbox  = pygame.Rect
        - data          = dict {str: hashable /pickle-able value}
        - parent_chunk_position = [int, int]
        - visible       = bool

        - collision_handling_method     = function
        """
        self.parent_chunk_position = parent.world_chunk_tile
        self.position = (x, y)
        self.world_hitbox = pygame.Rect(calculate_world_position(self.position, self.parent_chunk_position), (TILE_WIDTH, TILE_HEIGHT))
        self.handle_collision = handle_collision
        
        self.data = {}
        self.visible = True
        self.sprite_path = None
        self.sprite = None
    
    def set_sprite(self, path):
        """Set sprite path"""
        self.sprite_path = path
        self.sprite = pygame.transform.scale(Filehandler.get_image(self.sprite_path), (TILE_WIDTH, TILE_HEIGHT))
    
    def to_dict(self):
        """Convert tile to object that can be pickled - dict"""
        return {"pos": self.position, "path": self.sprite_path}


