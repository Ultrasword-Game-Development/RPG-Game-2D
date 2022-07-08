import pygame
from . import filehandler, entity, clock, maths

DEFAULT_WAIT_TIME = 1

PARTICLE_ID = 0
PARTICLE_X = 1          # x pos
PARTICLE_Y = 2          # y pos
PARTICLE_SXY = 3        # scale in x and y
PARTICLE_LIFE = 4       # lifetime
PARTICLE_MX = 5
PARTICLE_MY = 6


def DEFAULT_CREATE_FUNC(ph):
    """Creates a particle"""
    ph.p_count+=1
    ph.particles[ph.p_count] = [ph.p_count, ph.rect.x, ph.rect.y, 1, ph.start_life, maths.normalized_random()*10, maths.normalized_random()*10]

def DEFAULT_UPDATE_FUNC(ph, p, window):
    """Updates particles"""
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] <= 0:
        ph.rq.append(p[PARTICLE_ID])
        return
    # update position
    p[PARTICLE_X] += p[PARTICLE_MX] * clock.delta_time
    p[PARTICLE_Y] += p[PARTICLE_MY] * clock.delta_time
    # render
    pygame.draw.circle(window, ph.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)

class ParticleHandler(entity.Entity):
    """
    Particle Hanlder
    handles particles and renders them accordingly
    - can be textured or non-textured
    """
    def __init__(self):
        """
        Constructor for ParticleHandler
        contains:
        - particles             = {id: Particle}
        - texture               = pygame.Surface
        - color                 = [int, int, int, int]
        - start_life            = float

        - freq                  = float
        - decay                 = float
        - timer                 = clock.Timer
        """
        super().__init__()
        self.particles = {}
        self.rq = []
        self.p_count = 0

        self.create_func = DEFAULT_CREATE_FUNC
        self.update_func = DEFAULT_UPDATE_FUNC

        self.color = (255, 255, 255)
        self.decay = 0.1
        self.freq = DEFAULT_WAIT_TIME
        self.timer = clock.Timer(self.freq)
        self.start_life = 1.0

    def update(self):
        self.timer.update()
        if self.timer.changed:
            self.timer.changed = False
            self.create_func(self)

    def render(self, surface):
        """Update particles"""
        for particle in self.particles.values():
            self.update_func(self, particle, surface)
        for i in self.rq:
            self.particles.pop(i)
        self.rq.clear()

    def set_freq(self, freq):
        """Set new freq [1/freq]"""
        self.freq = freq
        self.timer.wait_time = freq
    
    def set_life(self, life):
        """Set new lifespan"""
        self.start_life = life
