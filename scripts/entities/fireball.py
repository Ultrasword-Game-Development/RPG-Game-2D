import pygame

from engine.misc import clock, maths
from engine.handler.scenehandler import SceneHandler
from engine import singleton as EGLOB
from engine.gamesystem import particle, entity
from engine.graphics import animation

from scripts import animationext, singleton, entityext
from scripts.game import skillhandler


# ---------- CONST VALUES ---------

ENTITY_NAME = "FIREBALL"
SKILL_NAME = "Fireball"

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

FIRE_PARTICLE_COLOR = (80, 10, 0)
FIRE_PARTICLE_FREQ = 1/20
FIRE_PARTICLE_LIFE = 3

CASTING_TIME = 2
COOLDOWN_TIME = 3
MANA_COST = 25

# -------- fire particle handler -------------- #

def particle_create(self):
    for item in self.parent.activeatk:
        if item not in self.parent.layer.handler.entities:
            continue
        self.p_count += 1
        self.particles[self.p_count] = self.parent.layer.handler.entity_buffer[item].create_particle(self.p_count)

def particle_update(self, p, surface):
    p[EGLOB.PARTICLE_LIFE] -= clock.delta_time
    if p[EGLOB.PARTICLE_LIFE] < 0:
        self.rq.append(p[EGLOB.PARTICLE_ID])
        return
    # update position
    p[EGLOB.PARTICLE_X] += p[EGLOB.PARTICLE_MX] * clock.delta_time
    p[EGLOB.PARTICLE_Y] += p[EGLOB.PARTICLE_MY] * clock.delta_time
    # render
    pygame.draw.circle(surface, self.color, (p[EGLOB.PARTICLE_X]+EGLOB.WORLD_OFFSET_X, p[EGLOB.PARTICLE_Y]+EGLOB.WORLD_OFFSET_Y), 1)


class FireParticleHandler(particle.ParticleHandler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_color(FIRE_PARTICLE_COLOR)
        self.set_freq(FIRE_PARTICLE_FREQ)
        self.set_life(FIRE_PARTICLE_LIFE)
        self.set_create_func(particle_create)
        self.set_update_func(particle_update)


# ----------- skill ------------------- #

class FireBallSkill(skillhandler.Skill):
    def __init__(self):
        super().__init__(SKILL_NAME, CASTING_TIME, COOLDOWN_TIME, MANA_COST)
    
    def activate(self, *args):
        return Fire(args[0], args[1])


# ------------ fire class ------------- #

class Fire(entityext.NonGameEntity):
    ANIM_CATEGORY = None
    ANGLE_CACHE = []

    def __init__(self, r_ent, phandler=None):
        super().__init__(ENTITY_NAME, r_ent)
        self.aregist = Fire.ANIM_CATEGORY.get_animation(FIRE_IDLE_ANIM).get_registry()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        # particle handler for smoke + embers
        if phandler:
            self.phandler = phandler
        else:
            self.phandler = FireParticleHandler(self)
        self.timer = clock.Timer(FIRE_PARTICLE_FREQ)
        # state handler for (creation + destruction + idle)
        # self.shandler = FireStateHandler(self)
        self.max_distance = DEFAULT_FIRE_MAX_DISTANCE
        self.distance_travelled = 0

    def start(self):
        pass

    def update(self):
        # standard stuff
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.aregist.angle = self.motion.angle_to(singleton.DOWN)
        self.aregist.update_angle()
        self.timer.update()
        if self.timer.changed:
            self.timer.changed = False
            self.phandler.create_particle()
        # movement
        self.position += self.motion
        self.move_to_position()
        # kill check
        self.distance_travelled += self.motion.magnitude()
        if self.distance_travelled > self.max_distance:
            self.rentity.remove_active_attack(self)
            self.kill()

    def render(self, surface):
        surface.blit(self.sprite, self.get_glob_pos())
        # entity.render_entity_hitbox(self, surface)
        # pygame.draw.rect(surface, (255,0,0), self.get_glob_cpos())

    def create_particle(self, pid):
        return [pid, self.rel_hitbox.centerx, self.rel_hitbox.centery, 1, FIRE_PARTICLE_LIFE, maths.normalized_random() * SMOKE_MOVE_SPEED, maths.normalized_random() * SMOKE_MOVE_SPEED]


# ------------- setup ----------- #
animationext.load_and_parse_aseprite_animation_wrotations("assets/particles/fire.json", 8)
Fire.ANIM_CATEGORY = animation.Category.get_category(FIRE_ANIM_CAT)
skillhandler.SkillHandler.add_skill(FireBallSkill())
entity.EntityTypes.register_entity_type(ENTITY_NAME, Fire)