import random
from math import sin
import pygame.transform as pgtrans

import soragl as SORA
from soragl import animation, physics, misc, smath

# -------------------------------------------------- #
# grass assets

class GrassAssets:
    # -------------------------------------------------- #
    # static
    ASSETS = {}

    @classmethod
    def get_asset(cls, file: str):
        if file not in cls.ASSETS:
            cls.ASSETS[file] = GrassAssets(file)
        return cls.ASSETS[file]

    # -------------------------------------------------- #
    # class

    def __init__(self, file: str):
        self._file = file
        self.rotation_range = (-80, 80, 20)
        # load animation
        self._animation = animation.Category.load_category(file)
        # original sequence
        self._sequence = animation.Category.get_category_framedata(file) # get the first animation registry
        self._sequence = list(self._sequence.values())[0]
        # rotate the sequence
        self._rsequence = animation.RotatedSequence(self._sequence, self.rotation_range)
        self._raregist = self._rsequence.get_registry()
        
        # variations
        self.rotations = (self.rotation_range[1] - self.rotation_range[0]) // self.rotation_range[2]
        self.var_length = len(self._sequence)
        print(self.var_length, self.rotations)
    
    def get_dimensions(self, image_set: int):
        """Get image dimensions for the i-th image set"""
        return self.dimensions[image_set]


# -------------------------------------------------- #
# grass handler
# each chunk will have a grass handler

G_POSITION = 0
G_ANGLE = 1
G_VARIATION = 2
G_ID = 3

GRASS_PARTICLE_HANDLER_SYSTEM = "grass-system"

class GrassHandler(physics.ParticleHandler):
    def __init__(self, grass_assets: str, grass_count: int = 100):
        super().__init__(max_particles=grass_count, handler_type=GRASS_PARTICLE_HANDLER_SYSTEM)
        self.assets = GrassAssets.get_asset(grass_assets)
        # add variables
        self["position"] = self.position
        self["area"] = self.area

    def on_ready(self):
        self.area = (self.world._options["chunkpixw"], self.world._options["chunkpixh"])
        super().on_ready()
        for i in range(5000):
            self.add_particle(self._create_func(self))


# particle handler functions
def _create_grass(parent, **kwargs):
    """Create a grass handler"""
    pos = parent.position + smath.random_range_vec2(parent.rect.width, parent.rect.height)
    return [
        pos,
        random.randint(parent.assets.rotation_range[0], parent.assets.rotation_range[1]),
        random.randint(0, parent.assets.var_length),
        parent.get_new_particle_id()
    ]

def _update_grass(parent, blade: list):
    """Update a grass blade"""
    blade[G_ANGLE] = sin(SORA.ENGINE_UPTIME + blade[G_POSITION].x) * 40 + 80
    # render grass
    # print(blade)
    # parent.assets.f = blade[G_VARIATION]
    # parent.assets._raregist.angle = blade[G_ANGLE]
    fdata = parent.assets._rsequence.get_frame_data(blade[G_VARIATION], blade[G_ANGLE])
    SORA.FRAMEBUFFER.blit(fdata.get_frame(), blade[G_POSITION] - (fdata.area[0]/2, fdata.area[1]/2) - SORA.OFFSET)

def _create_timer_grass(parent, **kwargs):
    pass

# register functions
physics.ParticleHandler.register_timer_function(GRASS_PARTICLE_HANDLER_SYSTEM, _create_timer_grass)
physics.ParticleHandler.register_create_function(GRASS_PARTICLE_HANDLER_SYSTEM, _create_grass)
physics.ParticleHandler.register_update_function(GRASS_PARTICLE_HANDLER_SYSTEM, _update_grass)

