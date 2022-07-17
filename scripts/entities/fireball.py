import pygame

from engine import *
from engine.globals import *

from scripts import animationext, singleton
from scripts.game import skillhandler


# ---------- CONST VALUES ---------

ENTITY_NAME = "FIREBALL"
SKILL_NAME = "FireBall"

# -------- animations ------------

FIRE_ANIM_CAT = "fire"
FIRE_IDLE_ANIM = "fire"

# --------- states ---------------



# --------------------------------

FIREBALL_ORIENTATION_COUNT = 8

MOVE_SPEED = 25
LERP_COEF = 0.3

DEFAULT_FIRE_MAX_DISTANCE = 150
SMOKE_MOVE_SPEED = 10


CASTING_TIME = 2
COOLDOWN_TIME = 3
MANA_COST = 25

# -------- fire particle handler -------------- #

def particle_create(self):
    self.p_count += 1
    # calculate x and y
    
    self.particles[self.p_count] = [self.p_count, self.parent.rect.centerx, self.parent.rect.centery, 1, self.start_life, maths.normalized_random() * SMOKE_MOVE_SPEED, maths.normalized_random() * SMOKE_MOVE_SPEED]

def particle_update(self, p, surface):
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] < 0:
        self.rq.append(p[PARTICLE_ID])
        return
    # update position
    p[PARTICLE_X] += p[PARTICLE_MX] * clock.delta_time
    p[PARTICLE_Y] += p[PARTICLE_MY] * clock.delta_time
    # render
    pygame.draw.circle(surface, self.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)


class FireParticleHandler(particle.ParticleHandler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_color((255, 0, 100))
        self.set_freq(1/20)
        self.set_life(5)
        self.set_create_func(particle_create)
        self.set_update_func(particle_update)


# ----------- skill ------------------- #

class FireBallSkill(skillhandler.Skill):
    def __init__(self):
        super().__init__(SKILL_NAME, CASTING_TIME, COOLDOWN_TIME, MANA_COST)
    
    def activate(self):
        return Fire()



# ------------ fire class ------------- #

class Fire(entity.Entity):
    ANIM_CATEGORY = None
    ANGLE_CACHE = []

    def __init__(self):
        super().__init__()
        self.aregist = Fire.ANIM_CATEGORY.get_animation(FIRE_IDLE_ANIM).get_registry()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        # particle handler for smoke + embers
        self.phandler = FireParticleHandler(self)
        # state handler for (creation + destruction + idle)
        # self.shandler = FireStateHandler(self)
        self.max_distance = DEFAULT_FIRE_MAX_DISTANCE
        self.distance_travelled = 0
        self.position = list(self.rect.center)

    def update(self):
        # standard stuff
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.aregist.angle = self.motion.angle_to(singleton.DOWN)
        self.aregist.update_angle()
        self.phandler.update()
        # kill check
        self.distance_travelled += self.motion.magnitude()
        if self.distance_travelled > self.max_distance:
            self.kill()
        # movement
        self.position[0] += self.motion.x
        self.position[1] += self.motion.y
        self.rect.center = list(map(int, self.position))

    def render(self, surface):
        surface.blit(self.sprite, self.rect)
        entity.render_entity_hitbox(self, surface)
        self.phandler.render(surface)

# ------------- setup ----------- #
animationext.load_and_parse_aseprite_animation_wrotations("assets/particles/fire.json", 8)
Fire.ANIM_CATEGORY = animation.Category.get_category(FIRE_ANIM_CAT)


