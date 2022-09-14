import pygame

from engine.misc import clock, maths
from engine import singleton
from engine.gamesystem import particle, entity
from engine.graphics import animation

from scripts import animationext, singleton as EGLOB, entityext
from scripts.events.attacks import Attack, generate_attack_data
from scripts.game import skillhandler

# -------------------------------------------------- #
animationext.load_and_parse_aseprite_animation_wrotations("assets/particles/fire.json", 8)


# -------------------------------------------------- #
# smoke particle handler

class SmokeParticleHandler(particle.ParticleHandler):
    DEFAULT_FIRE_MAX_DISTANCE = 150
    SMOKE_MOVE_SPEED = 10

    FIRE_PARTICLE_COLOR = (80, 10, 0)
    FIRE_PARTICLE_FREQ = 1 / 20
    FIRE_PARTICLE_LIFE = 3

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.set_color(SmokeParticleHandler.FIRE_PARTICLE_COLOR)
        self.set_freq(SmokeParticleHandler.FIRE_PARTICLE_FREQ)
        self.set_life(SmokeParticleHandler.FIRE_PARTICLE_LIFE)
        self.set_create_func(self._create)
        self.set_update_func(self._update)

    def _create(self):
        for item in self.parent.activeatk:
            if item not in self.parent.layer.handler.entities:
                continue
            self.p_count += 1
            self.particles[self.p_count] = self.parent.layer.handler.entity_buffer[item].create_particle(self.p_count)

    def _update(self, p, surface):
        p[singleton.PARTICLE_LIFE] -= clock.delta_time
        if p[singleton.PARTICLE_LIFE] < 0:
            self.rq.append(p[singleton.PARTICLE_ID])
            return
        # update position
        p[singleton.PARTICLE_X] += p[singleton.PARTICLE_MX] * clock.delta_time
        p[singleton.PARTICLE_Y] += p[singleton.PARTICLE_MY] * clock.delta_time
        # render
        pygame.draw.circle(surface, self.color,
                           (p[singleton.PARTICLE_X] + singleton.WORLD_OFFSET_X,
                            p[singleton.PARTICLE_Y] + singleton.WORLD_OFFSET_Y), 1)


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
    TYPE = "fire-attack"

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
