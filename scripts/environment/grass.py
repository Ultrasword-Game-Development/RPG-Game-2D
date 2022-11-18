import random
from math import sin

import pygame.transform

from engine import singleton as EGLOB
from engine.graphics import animation
from engine.misc import clock

from scripts import singleton, animationext, entityext


# -------------------------------------------------- #
# grass assets

class GrassAssets:
    # -------------------------------------------------- #
    # static
    ASSETS = {}

    @classmethod
    def get_asset(cls, name: str, file: str):
        if name not in cls.ASSETS:
            cls.ASSETS[name] = GrassAssets(file)
        return cls.ASSETS[name]

    # -------------------------------------------------- #
    # class

    def __init__(self, file: str):
        # load sprites from sprite-sheet
        self.info = animation.load_and_parse_aseprite_animation(file)
        self.aregist = animation.Category.get_category(self.info["cat"][0]).anims.values()
        self.aregist = list(self.aregist)[0].get_registry()
        self.images = [[] for i in range(self.aregist.parent.length)]
        self.load_range = (20, 160)
        self.skip = int(self.load_range[1] - self.load_range[0]) // 16
        for i in range(self.load_range[0], self.load_range[1], self.skip):
            angle = i
            for c in range(self.aregist.parent.length):
                self.images[c].append(pygame.transform.rotate(self.aregist.parent.frames[c].oframe, -angle))
        # variations
        self.variations = len(self.images)
        self.var_length = len(self.images[0])
        # get dimension data from each image set
        self.dimensions = [self.images[i][0].get_size() for i in range(len(self.images))]

    def get_dimensions(self, image_set: int):
        """Get image dimensions for the i-th image set"""
        return self.dimensions[image_set]

    def get_sprite(self, var: int, angle: float):
        return self.images[var][int(angle - self.load_range[0]) // self.skip]


# -------------------------------------------------- #
# grass handler
# each chunk will have a grass handler

class GrassHandler(entityext.NonGameEntity):
    def __init__(self, grass_assets: str):
        super().__init__("grass-handler", None)
        self.assets = GrassAssets.get_asset("general", grass_assets)
        self.aregist = self.assets.aregist

        # -------------------------------------------------- #
        # grass cache
        self.grass_count = 0
        self.grass = {}

        # ----------------------------------- #
        # wind effect
        self.wind_timer = clock.Timer(3)

    def update(self):
        # update the wind timer
        self.wind_timer.update()
        if self.wind_timer.changed:
            self.wind_timer.changed = False
            # now generate new wind instance
            pass

    def update_blade(self, blade: list):
        b = self.grass[blade]
        b[2] = sin(clock.run_time + b[0]) * 30 - 45
        # print(b[2])

    def render(self, surface):
        # update and render like particles
        cpos = self.get_glob_pos()
        for blade in self.grass:
            self.update_blade(blade)
            surface.blit(self.assets.get_sprite(self.grass[blade][3], self.grass[blade][2]),
                         (cpos[0] + self.grass[blade][0], cpos[1] + self.grass[blade][1]))

        # for i in range(self.assets.var_length):
        #     surface.blit(self.assets.images[0][i], (EGLOB.WORLD_OFFSET_X + i * 16, EGLOB.WORLD_OFFSET_Y))

    def debug(self, surface):
        pass

    def add_grass(self, x, y, i_orientation=0):
        self.grass_count += 1
        self.grass[self.grass_count] = [x, y, int(i_orientation), random.randint(0, self.assets.variations - 1)]
