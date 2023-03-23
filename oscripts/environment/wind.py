import pygame
import random
import math

from engine.misc import clock, maths

from scripts import entityext
from scripts.environment import ambient


# ----------------------------------- #
# wind class

class Wind(entityext.NonGameEntity):
    DEBUG_COLOR = (90, 200, 255)

    # ----------------------------------- #
    def __init__(self, angle: float, speed: float, power: float):
        """angle: wind direction in degrees"""
        super().__init__("wind-handler", None)
        # get normalized wind angle
        self.angle = math.radians(maths.__mod__(angle, 360))
        # find the slope of the linear function
        self.motion[0] = math.cos(self.angle)
        self.motion[1] = math.sin(self.angle)
        # creating linear function basically - y int increments each update :)
        self.y_int = 0
        # wind speed + power
        self.speed = speed
        self.power = power

    def start(self):
        # set position to camera left
        self.position.xy = (self.layer.camera.viewport.left - self.power, self.layer.camera.viewport.centery)

    def update(self):
        # move the wind object to the right
        self.position.x += self.motion[0] * self.speed * clock.delta_time
        self.position.y += self.motion[1] * self.speed * clock.delta_time

        # update position
        self.move_to_position()
        # print(self.position)

    def render(self, surface):
        pass

    def debug(self, surface):
        pygame.draw.circle(surface, Wind.DEBUG_COLOR, self.get_glob_pos(), self.power, 1)

    def power_at(self, point):
        """Find the power of the wind at a certain point"""
        return self.position.distance_to(point) / self.power

    def __hash__(self):
        return self.id


# ----------------------------------- #
# wind handler

class WindHandler(ambient.AmbienceSystem):
    # ----------------------------------- #
    # constants

    # ----------------------------------- #
    def __init__(self):
        super().__init__()
        self.winds = set()

    def add_wind(self, wind):
        """Add a new wind object to the wind array"""
        self.winds.add(wind)
        wind.layer = self.layer

    def remove_wind(self, wind):
        """Remove a wind from the array"""
        self.winds.remove(wind)

    def handle(self, surface):
        for wind in self.winds:
            wind.update()
            wind.render(surface)

    def debug(self, surface):
        for wind in self.winds:
            wind.debug(surface)

    def affect_function(self, affected):
        """
        Function that allows systems to interact with world
        <affected> = an entity or other system
        """
        for wind in self.winds:
            e = self.layer.handler.get_entity(wind)
            if e.power_at(affected.position) > 1:
                continue
            # handle interaction

