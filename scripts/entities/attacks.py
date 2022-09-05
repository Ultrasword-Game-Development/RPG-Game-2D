from engine.misc import clock
from engine.graphics import animation
from .particle_scripts import AnimatedParticle


# ---------------------------- #
# melee attacks

class MeleeStab(AnimatedParticle):
    def __init__(self, x, y, registry):
        super().__init__(x, y, registry)

    def update(self):
        super().update()
        self.position += self.motion * clock.delta_time
        self.rect.x += self.position.x
        self.rect.y += self.position.y
        self.motion *= 0.8
        # print(self.motion)

class RangedAttack(AnimatedParticle):
    def __init__(self, x, y, registry):
        pass


# ---------------------------- #
# ranged attacks

