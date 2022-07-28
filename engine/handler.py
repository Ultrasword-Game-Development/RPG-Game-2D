import pygame
from . import world, scenehandler

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
        self.entities = set()
        self.to_add = []
        self.to_remove = []

        # world
        self.world = world.World()
    
    def handle_entities(self, window):
        """Update and render entities to supplied window"""
        for i in self.entities:
            self.entity_buffer[i].update()
            self.entity_buffer[i].render(window)
        self.handle_changes()
    
    def add_entity(self, entity):
        """Add an entity"""
        entity.group = self
        self.to_add.append(entity)
    
    def handle_changes(self):
        """Handles adding + removal of entities"""
        for entity in self.to_add:
            self.entity_buffer[entity.id] = entity
            self.entities.add(entity.id)
            scenehandler.SceneHandler.CURRENT.world.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).add_entity(entity)
        for eid in self.to_remove:
            entity = self.entity_buffer[eid]
            self.entity_buffer[eid] = None
            self.entities.remove(eid)
            scenehandler.SceneHandler.CURRENT.world.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).remove_entity(entity)
        self.to_add.clear()
        self.to_remove.clear()

    def remove_entity(self, i):
        """Remove an entity"""
        self.to_remove.append(i)

    def get_world(self):
        """Get world object"""
        return self.world



