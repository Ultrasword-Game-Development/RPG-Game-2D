import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

from scripts import singleton

# -------------------------------------------------- #
# standard for generating attack data

def generate_attack_data(
    name: str,
    mana_cost: float,
    damage: float,
    penetration: float,
):
    """Generate attack data"""
    return {
        "name": name,
        "mana_cost": mana_cost,
        "damage": damage,
        "penetration": penetration,
    }

# -------------------------------------------------- #
# attack class

# signals
HIT_SIGNAL = "-hit"

class Attack(physics.Entity):
    def __init__(self, position: tuple, aregist: "Animation Register", data: dict={}, sender=None):
        super().__init__()
        self.data = data
        self.sender = sender
        self._aregist = aregist
        # signal
        self._hit_signal = signal.SignalRegister(HIT_SIGNAL)
    
    def on_ready(self):
        """Called when the attack is ready to be used"""
        # components)
        self.add_component(base_objects.AnimatedSprite(0, 0, self.aregist))
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(base_objects.Area2D(self.area[0], self.area[1]))

    def update(self):
        self._aregist.update()
        
    def debug(self, surface):
        super().debug(surface)
    
    # ------------------------------- #
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

# TODO - remove?
# # melee attacks
# class MeleeStab(Attack):

#     def __init__(self, x, y, registry, data, sender):
#         super().__init__(x, y, registry, data, sender)

#     def update(self):
#         super().update()
#         self.position += self.motion * clock.delta_time
#         self.rect.x += self.position.x
#         self.rect.y += self.position.y
#         self.motion *= 0.8
#         # print(self.motion)


# class RangedAttack(Attack):
#     def __init__(self, x, y, registry, data):
#         super().__init__(x, y, registry, data)

#     def update(self):
#         super().update()


# -------------------------------------------------- #
# setup

