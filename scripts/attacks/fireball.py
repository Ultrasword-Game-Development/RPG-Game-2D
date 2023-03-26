import pygame
from pygame import math as pgmath, draw as pgdraw

import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

# -------------------------------------------------- #

animation.Category.load_and_parse_aseprite_animation_wrotations("assets/particles/fire.json", 8)


# -------------------------------------------------- #
# smoke particle handler
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
particle.ParticleHandler.register_handler("fire", sph_create, sph_update)


# -------------------------------------------------- #
# skills

class FireBallSkill(skillhandler.Skill):
    # -------------------------------------------------- #
    # skill data
    SKILL_NAME = "Fireball"
    CASTING_TIME = 2
    COOLDOWN_TIME = 3
    MANA_COST = 25

    # -------------------------------------------------- #

    def __init__(self):
        super().__init__(FireBallSkill.SKILL_NAME, FireBallSkill.CASTING_TIME, FireBallSkill.COOLDOWN_TIME,
                         FireBallSkill.MANA_COST)

    def activate(self, *args):
        return Fire(args[0], args[1])


# -------------------------------------------------- #
# fire class

class Fire(Attack):
    # -------------------------------------------------- #
    # animation
    ANIM_CAT = "fire"

    IDLE_ANIM = "fire"

    # load
    ANIM_CATEGORY = animation.Category.get_category(ANIM_CAT)

    # -------------------------------------------------- #
    # states

    # -------------------------------------------------- #
    # statistics
    MS = 25
    LC = 0.3

    MAX_DISTANCE = 150

    FIREBALL_ORIENTATION_COUNT = 8

    # cdt

    # -------------------------------------------------- #
    # signals

    # wrappers

    # -------------------------------------------------- #
    # buffered objects
    ANGLE_CACHE = []

    # -------------------------------------------------- #

    def __init__(self, r_ent: entityext.GameEntity, phandler=None):
        super().__init__(r_ent.position.x, r_ent.position.y,
                         Fire.ANIM_CATEGORY.get_animation(Fire.IDLE_ANIM).get_registry(),
                         generate_attack_data(atk=5, pen=2), r_ent)
        self.name = Fire.TYPE
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        # particle handler for smoke + embers
        if phandler:
            self.phandler = phandler
        else:
            self.phandler = SmokeParticleHandler(self)
        # state handler for (creation + destruction + idle)
        # self.shandler = FireStateHandler(self)
        self.distance_travelled = 0

    def start(self):
        pass

    def update(self):
        # standard stuff
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.aregist.angle = self.motion.angle_to(EGLOB.DOWN)
        self.aregist.update_angle()

        self.phandler.update()

        # movement
        self.position += self.motion
        self.move_to_position()
        # kill check
        self.distance_travelled += self.motion.magnitude()
        if self.distance_travelled > Fire.MAX_DISTANCE and self.sender:
            self.sender.remove_active_attack(self)
            self.kill()

    def render(self, surface):
        surface.blit(self.sprite, self.get_glob_pos())
        # entity.render_entity_hitbox(self, surface)
        # pygame.draw.rect(surface, (255,0,0), self.get_glob_cpos())

    def create_particle(self, pid):
        return [pid, self.rel_hitbox.centerx, self.rel_hitbox.centery, 1, SmokeParticleHandler.FIRE_PARTICLE_LIFE,
                maths.normalized_random() * SmokeParticleHandler.SMOKE_MOVE_SPEED,
                maths.normalized_random() * SmokeParticleHandler.SMOKE_MOVE_SPEED]


# ------------- setup ----------- #
skillhandler.SkillHandler.add_skill(FireBallSkill())
entity.EntityTypes.register_entity_type(Fire.TYPE, Fire)
