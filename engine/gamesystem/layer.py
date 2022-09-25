"""
Layer system -- handles events according to layer
"""

from ..handler import handler, eventhandler
from ..world import world
from ..graphics import camera
from .. import singleton


class Layer:
    def __init__(self, scene):
        self.scene = scene
        # handlers
        self.handler = handler.Handler(self)
        self.world = world.World(self)
        self.camera = camera.Camera()

    def handle(self, surface):
        # print(self.camera.chunkpos)
        if singleton.DEBUG:
            self.world.debug_handle_chunks(surface, singleton.RENDER_DIS)
            self.handler.debug_handle_entities(surface)
        else:
            self.world.handle_chunks(surface, singleton.RENDER_DIS)
            self.handler.handle_entities(surface)


