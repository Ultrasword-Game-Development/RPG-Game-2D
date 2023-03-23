from engine.misc import clock
from scripts import singleton
from engine.handler.eventhandler import Event, Eventhandler
from scripts.entities.particle_scripts import AnimatedParticle


# -------------------------------------------------- #
# functions + callbacks

def generate_attack_data(**kwargs):
    return kwargs


def handle_hit(event):
    print("Handle Event:", event.data['a'].name, event.data['b'].name)


# create attack event
def create_attack_event(event):
    print(event.data)


# -------------------------------------------------- #
# attack class

class Attack(AnimatedParticle):
    # -------------------------------------------------- #
    # signals
    HIT_SIGNAL = "-hit"

    # wrappers
    HIT_WRAPPER = Eventhandler.register_to_signal(HIT_SIGNAL, handle_hit)

    # -------------------------------------------------- #

    def __init__(self, x, y, registry, data, sender=None):
        super().__init__(x, y, registry)
        self.data = data
        self.sender = sender

    def update(self):
        super().update()
        # check if hit an object
        for entity in self.layer.world.find_nearby_entities(self.chunk, 0):
            if entity.id == self.id or (self.sender and entity.id == self.sender.id):
                continue
            # TODO - swap out this is temporary
            if self.rel_hitbox.colliderect(entity.rel_hitbox):
                Eventhandler.emit_signal(Event(Attack.HIT_SIGNAL, {'a': self, 'b': entity}))

    def debug(self, surface):
        super().debug(surface)


# -------------------------------------------------- #


# melee attacks
class MeleeStab(Attack):

    def __init__(self, x, y, registry, data, sender):
        super().__init__(x, y, registry, data, sender)

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


# -------------------------------------------------- #
# setup

singleton.ATTACK_PARTICLE_CREATE = Eventhandler.register_to_signal(singleton.ATTACK_PARTICLE_CREATE_ID,
                                                                   create_attack_event)



