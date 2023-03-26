import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

from scripts import singleton


# -------------------------------------------------- #
# attack class

# signals
HIT_SIGNAL = "-hit"


class Attack(physics.Entity):
    def __init__(self, aregist, data: dict, sender=None):
        super().__init__()
        self.data = data
        self.sender = sender
        self._aregist = aregist
        # signal
        self._hit_signal = signal.SignalRegister(HIT_SIGNAL)
    
    def on_ready(self):
        """Called when the attack is ready to be used"""
        # components
        self.add_component(base_objects.AnimatedSprite(0, 0, self.aregist))
        self.add_component(base_objects.Area2D(self.area[0], self.area[1]))

    def update(self):
        # check if hit an object
        for entity in self.layer.world.find_nearby_entities(self.chunk, 0):
            if entity.id == self.id or (self.sender and entity.id == self.sender.id):
                continue
            # TODO - swap out this is temporary
            if self.rel_hitbox.colliderect(entity.rel_hitbox):
                Eventhandler.emit_signal(Event(Attack.HIT_SIGNAL, {'a': self, 'b': entity}))

    def debug(self, surface):
        super().debug(surface)
    
    @property
    def aregist(self):
        """Returns the animation registry"""
        return self._aregist
    
    @aregist.setter
    def aregist(self, value):
        """Sets the animation registry"""
        self._aregist = value
        self.get_component(base_objects.AnimatedSprite).aregist = value
        


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



