import pygame
from . import world

class Handler:
    """
    Handles all pygame.sprite.Sprite objects
    - update + render
    """
    def __init__(self):
        """
        Handler Constructor
        - stores arrays of pygame.sprite.Group objects
        """
        self.entity_buffer = {}
        self.entities = []

        # world
        self.world = world.World()
    
    def handle_entities(self, window):
        """Update and render entities to supplied window"""
        for i in self.entities:
            self.entity_buffer[i].update()
            self.entity_buffer[i].render(window)
    
    def add_entity(self, entity):
        """Add an entity"""
        entity.group = self
        self.entity_buffer[entity.id] = entity
        self.entities.append(entity.id)
    
    def remove_entity(self, i):
        """Remove an entity"""
        self.entities[i].dead = True
    
    def get_world(self):
        """Get world object"""
        return self.world



