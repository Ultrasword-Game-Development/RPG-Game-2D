import pygame

from engine import *
from scripts import animationext, singleton



# ---------- CONST VALUES ---------

ENTITY_NAME = "FIREBALL"

# -------- animations ------------

FIRE_ANIM_CAT = "fire"
FIRE_IDLE_ANIM = "fire"

# --------- states ---------------



# --------------------------------

FIREBALL_ORIENTATION_COUNT = 8

MOVE_SPEED = 25
LERP_COEF = 0.3


# -------- fire particle handler -------------- #

def particle_create(self):
    self.p_count += 1
    # calculate x and y
    theta = maths.normalized_random() * 3.14
    x = maths.math.sin(theta)*MAGE_PREFERED_DISTANCE + self.parent.rel_hitbox.centerx
    y = maths.math.cos(theta)*MAGE_PREFERED_DISTANCE + self.parent.rel_hitbox.centery
    self.particles[self.p_count] = [self.p_count, x, y, 1, self.start_life, 0, 0]

def particle_update(self, p, surface):
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] < 0:
        self.rq.append(p[PARTICLE_ID])
        return
    # update position
    off = pygame.math.Vector2(self.parent.rel_hitbox.centerx - p[PARTICLE_X], self.parent.rel_hitbox.centery - p[PARTICLE_Y])
    off.normalize_ip()
    p[PARTICLE_MX] += off.x * clock.delta_time
    p[PARTICLE_MY] += off.y * clock.delta_time

    p[PARTICLE_X] += p[PARTICLE_MX]
    p[PARTICLE_Y] += p[PARTICLE_MY]
    # render
    pygame.draw.circle(surface, self.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)


class FireParticleHandler(particle.ParticleHandler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_color((255, 0, 100))
        self.set_freq(1/20)
        self.set_life(2)
        self.set_create_func(particle_create)
        self.set_update_func(particle_update)
    
    def update(self):
        pass


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

    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.motion.x += MOVE_SPEED * clock.delta_time
        self.motion.y += MOVE_SPEED * clock.delta_time
        self.aregist.angle = self.motion.angle_to(singleton.DOWN)
        self.aregist.update_angle()

        self.rect.centerx += round(self.motion.x)
        self.rect.centery += round(self.motion.y)
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite, self.rect)

# ------------- setup ----------- #
animationext.load_and_parse_aseprite_animation_wrotations("assets/particles/fire.json", 8)
Fire.ANIM_CATEGORY = animation.Category.get_category(FIRE_ANIM_CAT)


