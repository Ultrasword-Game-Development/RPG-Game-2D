import pygame
from .. import singleton as EGLOB
from ..misc import maths
from .. import singleton


class Camera:
    def __init__(self):
        """
        Camera Constructor:
        contains:
        - position
        """
        self.campos = pygame.math.Vector2(0, 0)
        self.position = pygame.math.Vector2(0, 0)
        self.chunkpos = [0, 0]
        self.screenchunkpos = [0, 0]
        # ----------------------------------- #
        # viewport size
        self.viewport = pygame.rect.Rect(0, 0, EGLOB.FB_WIDTH, EGLOB.FB_HEIGHT)

        # target info + cache
        self.target = None

    def track_target(self):
        """Track an entity target and center them"""
        if not self.target:
            return
        # get world position
        wpos = self.target.rel_hitbox
        # set position
        self.position.x = self.campos.x + EGLOB.FBWHALF
        self.position.y = self.campos.y + EGLOB.FBHHALF
        # chunk pos
        self.screenchunkpos[0] = int(self.campos.x) // singleton.CHUNK_PIX_WIDTH
        self.screenchunkpos[1] = int(self.campos.y) // singleton.CHUNK_PIX_HEIGHT
        self.chunkpos[0] = -self.screenchunkpos[0]
        self.chunkpos[1] = -self.screenchunkpos[1]
        # viewport position
        self.viewport.topleft = -self.position.xy

    def set_target(self, target):
        """Set a target"""
        self.target = target

    def update(self):
        """Updates EGLOB Offsets"""
        EGLOB.WORLD_OFFSET_X = self.position.x
        EGLOB.WORLD_OFFSET_Y = self.position.y
    
    def get_target_rel_pos(self):
        """Get the raget relative position"""
        return EGLOB.FBWHALF - self.target.rect.width // 2, EGLOB.FBHHALF - self.target.rect.height // 2


