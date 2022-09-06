import pygame
from . import scenehandler

from ..gamesystem import entity


class Handler:
    """
    Handles all pygame.sprite.Sprite objects
    - update + render
    """
    def __init__(self, layer):
        """
        Handler Constructor
        - stores arrays of pygame.sprite.Group objects
        """
        self.entity_buffer = {}
        self.entities = set()
        self.to_add = []
        self.to_remove = []

        # world
        self.layer = layer
        self.scene = layer.scene
    
    def handle_entities(self, window):
        """Update and render entities to supplied window"""
        for i in self.entities:
            self.entity_buffer[i].update()
            if i not in self.to_remove:
                self.entity_buffer[i].render(window)
        self.handle_changes()
    
    def debug_handle_entities(self, window):
        """Update and render entities to supplied window + debug"""
        for i in self.entities:
            self.entity_buffer[i].update()
            if i not in self.to_remove:
                self.entity_buffer[i].render(window)
            self.entity_buffer[i].debug(window)
        self.handle_changes()

    def add_entity(self, entity):
        """Add an entity"""
        entity.layer = self.layer
        entity.start()
        self.to_add.append(entity)

    def get_entity(self, eid):
        """Get an entity"""
        return self.entity_buffer[eid]

    def handle_changes(self):
        """Handles adding + removal of entities"""
        for entity in self.to_add:
            self.entity_buffer[entity.id] = entity
            self.entities.add(entity.id)
            self.layer.world.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).add_entity(entity)
        for eid in self.to_remove:
            entity = self.entity_buffer[eid]
            self.entity_buffer[eid] = None
            self.entities.remove(eid)
            self.layer.world.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).remove_entity(entity)
        self.to_add.clear()
        self.to_remove.clear()

    def remove_entity(self, i):
        """Remove an entity"""
        self.to_remove.append(i)



