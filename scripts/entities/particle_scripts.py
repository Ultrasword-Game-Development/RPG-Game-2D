from engine.gamesystem import particle
from engine.gamesystem.particle import *

from engine.misc import maths, clock
from engine.graphics import animation

from .. import singleton

from .. import entityext


def GRAVITY_PARTICLE_CREATE(ph):
    ph.p_count += 1
    ph.particles[ph.p_count] = [ph.p_count, ph.rect.x, ph.rect.y, 1, ph.start_life, maths.normalized_random() * 10,
                                -40 - 50 * maths.np.random.random()]


def GRAVITY_PARTICLE_UPDATE(ph, p, window):
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] <= 0:
        ph.rq.append(p[PARTICLE_ID])
        return
    # update position
    p[PARTICLE_MY] += singleton.GRAVITY * clock.delta_time
    # interact with player
    player = ph.data['player']
    # move x
    p[PARTICLE_X] += p[PARTICLE_MX] * clock.delta_time
    if player.rel_hitbox.collidepoint(int(p[PARTICLE_X]), int(p[PARTICLE_Y])):
        if p[PARTICLE_MX] > 0:
            p[PARTICLE_X] = player.rel_hitbox.left - 0.5
        elif p[PARTICLE_MX] < 0:
            p[PARTICLE_X] = player.rel_hitbox.right + 0.5
        p[PARTICLE_MX] *= -0.3

    # move y
    p[PARTICLE_Y] += p[PARTICLE_MY] * clock.delta_time
    if player.rel_hitbox.collidepoint(int(p[PARTICLE_X]), int(p[PARTICLE_Y])):
        # check for which side
        if p[PARTICLE_MY] > 0:
            p[PARTICLE_Y] = player.rel_hitbox.top - 0.5
        elif p[PARTICLE_MY] < 0:
            p[PARTICLE_Y] = player.rel_hitbox.bottom + 0.5
        p[PARTICLE_MY] *= -0.3

    if p[PARTICLE_Y] > ph.rect.y:
        p[PARTICLE_Y] = ph.rect.y
        p[PARTICLE_MY] = -abs(p[PARTICLE_MY]) * 0.3
    # render
    pygame.draw.circle(window, ph.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)


# animated particle
ANIMATED_NAME = "ani_p"


class AnimatedParticle(entityext.NonGameEntity):
    def __init__(self, x, y, registry):
        super().__init__(ANIMATED_NAME, None)
        # set position
        self.rect.center = (x, y)
        self.aregist = registry

    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        if self.aregist.has_finished():
            self.kill()

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, 1, 0),
                     self.get_glob_pos())
