import pygame
from pygame import math as pgmath, draw as pgdraw

import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

from scripts.attacks import attacks
from scripts.game import skillhandler

# -------------------------------------------------- #
# smoke particle handler
SPH_HANDLER_TYPE = 'SPH_DEFAULT_NAME'
SPH_DEFAULT_FIRE_MAX_DISTANCE = 150
SPH_SMOKE_MOVE_SPEED = 10
SPH_RADIUS = 1

SPH_FIRE_PARTICLE_COLOR = (80, 10, 0)
SPH_FIRE_PARTICLE_FREQ = 1 / 20
SPH_FIRE_PARTICLE_LIFE = 3

SPH_POSITION = 0
SPH_VELOCITY = 1
SPH_LIFE = 2
SPH_RADIUS = 3
SPH_ID = 4

def sph_create(parent, **kwargs):
    """Create a new particle."""
    return [
        pgmath.Vector2(parent.position.xy),
        pgmath.Vector2(smath.normalized_random(),smath.normalized_random()).normalize() * SPH_SMOKE_MOVE_SPEED * smath.normalized_random(),
        SPH_FIRE_PARTICLE_LIFE,
        SPH_RADIUS,
        parent.get_new_particle_id()
    ]

def sph_update(particle, surface):
    """Update a particle."""
    particle[SPH_LIFE] -= clock.delta_time
    if particle[SPH_LIFE] < 0:
        particle[SPH_ID] = None
        return
    # update position
    particle[SPH_POSITION] += particle[SPH_VELOCITY] * clock.delta_time
    # render
    pgdraw.circle(surface, SPH_FIRE_PARTICLE_COLOR,
                    (particle[SPH_POSITION].x + SORA.OFFSET[0],
                    particle[SPH_POSITION].y + SORA.OFFSET[1]), 
                    particle[SPH_RADIUS])

# register
physics.ParticleHandler.register_particle_type(SPH_HANDLER_TYPE, sph_create, sph_update)


# -------------------------------------------------- #
# skills

# skill data
FB_SKILL_NAME = "Fireball"
FB_CASTING_TIME = 2
FB_COOLDOWN_TIME = 3
FB_MANA_COST = 25

class FireBallSkill(skillhandler.Skill):
    def __init__(self):
        super().__init__(FB_SKILL_NAME, FB_CASTING_TIME, FB_COOLDOWN_TIME,
                        FB_MANA_COST)

    def activate(self, *args):
        return Fire(args[0], args[1])


# -------------------------------------------------- #
# fire class

# animation
F_ANIM_CAT = "assets/particles/fire.json"
F_IDLE_ANIM = "fire"
F_FIREBALL_ORIENTATION_COUNT = 8
F_ANGLE_RANGE = (0, 360, 360//F_FIREBALL_ORIENTATION_COUNT)

animation.Category.load_category(F_ANIM_CAT)
F_ANIM_CACHE = animation.RotatedSequence(animation.Category.get_category_framedata(F_ANIM_CAT)[F_IDLE_ANIM], angle_range=F_ANGLE_RANGE)

# statistics
F_MS = 25
F_LC = 0.3
F_MAX_DISTANCE = 150

class Fire(attacks.Attack):
    def __init__(self, sender: "Entity"):
        super().__init__(sender.position.xy, F_ANIM_CACHE.get_registry(), sender=sender)
        # private
        self._distance_travelled = 0
        self._phandler = physics.ParticleHandler(handler_type=SPH_HANDLER_TYPE)
        self._phandler.position = self.position

    def on_ready(self):
        super().on_ready()

    def update(self):
        super().update()
        self.aregist.angle = self.motion.angle_to(physics.World2D.UP)

        # kill check
        self.distance_travelled += self.velocity.magnitude()
        if self.distance_travelled > Fire.MAX_DISTANCE:
            self.kill()

# ------------- setup ----------- #
skillhandler.SkillHandler.add_skill(FireBallSkill())
