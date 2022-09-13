from engine.misc import clock
from engine.graphics import animation
from engine.handler.eventhandler import Event, Eventhandler
from .particle_scripts import AnimatedParticle


# -------------------------------------------------- #

def generate_attack_data(**kwargs):
    return kwargs


def handle_hit(event):
    print(event.data['a'].name, event.data['b'].name)


# -------------------------------------------------- #
# attack class

class Attack(AnimatedParticle):
    # -------------------------------------------------- #
    # signals
    HIT_SIGNAL = "-hit"

    # wrappers
    HIT_WRAPPER = Eventhandler.register_to_signal(HIT_SIGNAL, handle_hit)

    # -------------------------------------------------- #

    def __init__(self, x, y, registry, data):
        super().__init__(x, y, registry)
        self.data = data

    def update(self):
        super().update()
        # check if hit an object
        for entity in self.layer.world.find_nearby_entities(self.chunk, 0):
            if entity.id == self.id:
                continue
            if self.rel_hitbox.colliderect(entity.rel_hitbox):
                Eventhandler.emit_signal(Event(Attack.HIT_SIGNAL, {'a': self, 'b': entity}))


# -------------------------------------------------- #


# melee attacks
class MeleeStab(Attack):
    def __init__(self, x, y, registry, data):
        super().__init__(x, y, registry, data)

    def update(self):
        super().update()
        self.position += self.motion * clock.delta_time
        self.rect.x += self.position.x
        self.rect.y += self.position.y
        self.motion *= 0.8
        # print(self.motion)


class RangedAttack(Attack):
    def __init__(self, x, y, registry, data):
        super().__init__(x, y, registry, data)

    def update(self):
        super().update()

# ---------------------------- #
# ranged attacks
