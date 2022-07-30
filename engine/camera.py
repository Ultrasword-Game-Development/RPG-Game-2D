import pygame
from . import singleton as EGLOB


class Camera:
    def __init__(self):
        """
        Camera Constructor:
        contains:
        - position
        """
        self.campos = pygame.math.Vector2(0, 0)
        self.position = pygame.math.Vector2(0, 0)

        # target info + cache
        self.target = None

    def track_target(self):
        """Track an entity target and center them"""
        if not self.target:
            return
        # get world position
        wpos = self.target.rel_hitbox
        self.position.x = self.campos.x + EGLOB.FBWHALF
        self.position.y = self.campos.y + EGLOB.FBHHALF

    def set_target(self, target):
        """Set a target"""
        self.target = target

    def update(self):
        """Updates EGLOB Offsets"""
        EGLOB.WORLD_OFFSET_X = self.position.x
        EGLOB.WORLD_OFFSET_Y = self.position.y
    
    def get_target_rel_pos(self):
        """Get the raget relative position"""
        return (EGLOB.FBWHALF - self.target.rect.width//2, EGLOB.FBHHALF - self.target.rect.height//2)


