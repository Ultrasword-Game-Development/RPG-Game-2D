import pygame
from engine import world, chunk

from engine.scenehandler import SceneHandler as SH

class RPGWorld(world.World):
    """
    A world which contains:
    - entities
    - structures
    - environment
    """
    def __init__(self, scene, bg_col = (255, 255, 255)):
        """
        Constructor for RPGWorld
        - should be able to save and be loaded
        - contains chunks
        """
        super().__init__(scene)
        self.bg_col = bg_col


class RPGChunk(chunk.Chunk):
    """
    A chunk that contains:
    - entities
    - structures
    - environment
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tilemap = None

    def render(self, surface, offset=(0,0)):
        """Render function"""
        for env in self.environment:
            env.render(surface, offset)


