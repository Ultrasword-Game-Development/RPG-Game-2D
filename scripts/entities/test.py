import pygame

from engine import entity, clock, maths, scenehandler
from engine import animation, user_input, camera
from engine import singleton as EGLOB

from scripts import entityext, singleton

ENTITY_NAME = "test"

class Test(entityext.GameEntity):
    def __init__(self):
        super().__init__(ENTITY_NAME, 100, 100)
        self.position.xy = (100, 100)
        self.vec = pygame.math.Vector2(singleton.UP)

    def update(self):
        self.vec.rotate_ip(90 * clock.delta_time)
        self.position += self.vec
        

    def render(self, surface):
        pygame.draw.line(surface, (255,0,0), self.position, self.position+singleton.UP * 10)
        pygame.draw.line(surface, (255, 100, 0), self.position, self.position + self.vec*10)
