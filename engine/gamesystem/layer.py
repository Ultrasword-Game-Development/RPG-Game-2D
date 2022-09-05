"""
Layer system -- handles events according to layer
"""

from ..handler import handler
from ..world import world

class Layer:
    def __init__(self, scene):
        self.scene = scene
        # handlers
        self.handler = handler.Handler(self)
        self.world = world.World(self)
    
    def handle(self, surface):
        self.handler.handle_entities(surface)
        self.world.handle_chunks(surface)
    
    def handle_signal(self, signal):
        pass

