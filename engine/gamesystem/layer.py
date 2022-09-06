"""
Layer system -- handles events according to layer
"""

from ..handler import handler
from ..world import world
from ..graphics import camera


class Layer:
    def __init__(self, scene):
        self.scene = scene
        # handlers
        self.handler = handler.Handler(self)
        self.world = world.World(self)
        self.camera = camera.Camera()

    def handle(self, surface, debug=False):
        if debug:
            self.handler.debug_handle_entities(surface)
        else:
            self.handler.handle_entities(surface)
        self.world.handle_chunks(surface, self.camera.chunkpos)
    
    def handle_signal(self, signal):
        pass

