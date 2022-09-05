import pygame

from engine.gamesystem import entity
from engine.graphics import camera, animation
from engine.misc import clock, maths
from engine.handler import scenehandler
from engine import singleton as EGLOB

from scripts import entityext, singleton

ENTITY_NAME = "test"

class Test(entityext.NonGameEntity):
    def __init__(self):
        super().__init__(ENTITY_NAME, None)
        # self.position.xy = (100, 100)
        self.vec = pygame.math.Vector2(singleton.UP)
        self.start = pygame.math.Vector2(self.position)

    def update(self):
        self.vec.rotate_ip(90 * clock.delta_time)
        self.position += self.vec

    def render(self, surface):
        pygame.draw.line(surface, (255,0,0), self.position+self.get_glob_cpos(), self.position+singleton.UP * 10+self.get_glob_cpos())
        pygame.draw.line(surface, (255, 100, 0), self.position+self.get_glob_cpos(), self.position + self.vec*10+self.get_glob_cpos())
        pygame.draw.circle(surface, (255, 0, 0), self.start+self.get_glob_cpos(), 1)


class TrailTest(entityext.NonGameEntity):
    def __init__(self):
        super().__init__("trailtest", None)
        self.timer = clock.Timer(2.0)
    
    def update(self):
        self.timer.update()
        if self.timer.changed:
            self.kill()
        self.rect.topleft = self.position.xy
    
    def render(self, surface):
        pygame.draw.circle(surface, (0, 0, 255), self.position+self.get_glob_cpos(), 1)


