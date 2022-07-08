from engine import particle
from engine import maths, clock

from engine.particle import *
from ..globals import *


def GRAVITY_PARTICLE_CREATE(ph):
    ph.p_count+=1
    ph.particles[ph.p_count] = [ph.p_count, ph.rect.x, ph.rect.y, 1, ph.start_life, maths.normalized_random()*10, -40-50*maths.np.random.random()]


def GRAVITY_PARTICLE_UPDATE(ph, p, window):
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] <= 0:
        ph.rq.append(p[PARTICLE_ID])
        return
    # update position
    p[PARTICLE_MY] += GRAVITY * clock.delta_time
    p[PARTICLE_X] += p[PARTICLE_MX] * clock.delta_time
    p[PARTICLE_Y] += p[PARTICLE_MY] * clock.delta_time
    if p[PARTICLE_Y] > ph.rect.y:
        p[PARTICLE_Y] = ph.rect.y
        p[PARTICLE_MY] = -abs(p[PARTICLE_MY]) * 0.3
    # render
    pygame.draw.circle(window, ph.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)






