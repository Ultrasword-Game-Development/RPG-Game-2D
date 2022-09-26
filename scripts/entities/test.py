import pygame

from engine.gamesystem import entity
from engine.graphics import camera, animation
from engine.misc import clock, maths
from engine.handler import scenehandler, filehandler
from engine import singleton as EGLOB

from scripts import entityext, singleton

ENTITY_NAME = "test"


class Test(entityext.NonGameEntity):
    def __init__(self):
        super().__init__(ENTITY_NAME, None)
        # self.position.xy = (100, 100)
        self.vec = pygame.math.Vector2(singleton.UP)
        self.start_pos = pygame.math.Vector2(self.position)

        self.test_angle = 0
        self.test_img = filehandler.Filehandler.get_image("assets/sprites/grass.png").subsurface((0, 0, 16, 16))

    def start(self):
        pass

    def update(self):
        self.vec.rotate_ip(90 * clock.delta_time)
        self.position += self.vec

        self.test_angle += 30 * clock.delta_time

    def render(self, surface):
        surface.blit(pygame.transform.rotate(self.test_img, -self.test_angle).convert(), (EGLOB.WORLD_OFFSET_X-50, EGLOB.WORLD_OFFSET_Y))
        pygame.draw.line(surface, (255,0,0), self.position+self.get_glob_cpos(), self.position+singleton.UP * 10+self.get_glob_cpos())
        pygame.draw.line(surface, (255, 100, 0), self.position+self.get_glob_cpos(), self.position + self.vec*10+self.get_glob_cpos())
        pygame.draw.circle(surface, (255, 0, 0), self.start_pos+self.get_glob_cpos(), 1)


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


