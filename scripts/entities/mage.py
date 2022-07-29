import pygame
from engine import entity, clock, maths
from engine import animation, user_input
from engine import statehandler, particle, scenehandler

from engine.globals import *


from scripts import singleton, entityext, skillext, animationext
from scripts.game import state, skillhandler
from scripts.entities import fireball

# ---------- CONST VALUES ---------

ENTITY_NAME = "MAGE"
MAGE_HEALTH = 100
MAGE_MANA = 100

# -------- animations ------------

MAGE_ANIM_CAT = "mage"
MAGE_IDLE_ANIM = "idle"
MAGE_RUN_ANIM = "run"
MAGE_PRECAST_ANIM = "pre_attack"
MAGE_CASTING_ANIM = "casting"
MAGE_POSTCAST_ANIM = "end_cast"

# --------- states ---------------

MAGE_IDLE_STATE = "idle"
MAGE_ALERT_STATE = "alert"
MAGE_FLIGHT_STATE = "flight"
MAGE_PRECAST_STATE = "precast"
MAGE_CASTING_STATE = "casting"
MAGE_POSTCAST_STATE = "postcast"
MAGE_ATTACK_STATE = "firing"

# --------------------------------

MOVE_SPEED = 20
LERP_COEF = 0.3


MAGE_DETECT_RADIUS = 130
MAGE_PREFERED_DISTANCE = 70
MAGE_CRITICAL_DEF_DISTANCE = 30


PLERP_COEF = 0.97
MAGE_PARTICLE_SPAWN_RADIUS = MAGE_CRITICAL_DEF_DISTANCE
MAGE_PARTICLE_LIFE = 2.0
MAGE_PARTICLE_FREQ = 30
MAGE_PARTICLE_COLOR = (255, 0, 100)

# ---------- CDR TIMES ------------

MAGE_ALERT_PRECAST_CDR = 1.0
MAGE_DEFAULT_CASTING_CDR = 2.3

# ---------- MAGE SKILLS ---------

MAGE_SKILL_TREE = skillhandler.SkillTree(skillext.SkillTreeLoader("assets/skilltree/mage.json"))

SKILL_FIREBALL = fireball.FireBallSkill()

MAGE_SKILLS = skillhandler.SkillHandler()
MAGE_SKILLS.add_skill(SKILL_FIREBALL)


# TODO:
# 1. cooldown timer  for attacks

# --------- mage state handler ---------- #

class IdleState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_IDLE_STATE, parent)

    def start(self):
        self.parent.aregist[MAGE_IDLE_ANIM].f_num = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, MAGE_IDLE_ANIM)
        # check for player distance etc
        if self.handler.player_dis < MAGE_DETECT_RADIUS:
            self.handler.set_active_state(MAGE_ALERT_STATE)
        # also calculate for idle movement

class AlertState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_ALERT_STATE, parent)
        self.countdown = MAGE_ALERT_PRECAST_CDR

    def start(self):
        # print("alert")
        self.countdown = MAGE_ALERT_PRECAST_CDR

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, MAGE_IDLE_ANIM)

        # case 1: timer counts to 0
        self.countdown -= clock.delta_time
        if self.countdown <= 0:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(MAGE_PRECAST_STATE)
        # case 2: player comes too close
        if self.handler.player_dis < MAGE_PREFERED_DISTANCE:
            # case 2 fulfilled, begin flight
            self.handler.set_active_state(MAGE_FLIGHT_STATE)
        # case 3: player goes out of range
        elif self.handler.player_dis > MAGE_DETECT_RADIUS:
            # case 3 fulfilled, begin idle
            self.handler.set_active_state(MAGE_IDLE_STATE)

class PrecastState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_PRECAST_STATE, parent)
    
    def start(self):
        # print("starting precast")
        self.parent.aregist[MAGE_PRECAST_ANIM].fini = 0
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, MAGE_PRECAST_ANIM)

        # case 1: finish precast
        if self.parent.aregist[MAGE_PRECAST_ANIM].fini > 0:
            # case 1 fulfilled, begin casting
            self.handler.set_active_state(MAGE_CASTING_STATE)
        # case 2: what if casting fails? what if player interrupts?

class CastingState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_CASTING_STATE, parent)
        self.casting_cdr = MAGE_DEFAULT_CASTING_CDR
    
    def start(self):
        # print("casting spell")
        self.casting_cdr = MAGE_DEFAULT_CASTING_CDR
        # decide on an attack and set casting_cdr depending on attack
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, MAGE_CASTING_ANIM)

        self.parent.phandler.create_particle()
        # case 1: finish casting
        self.casting_cdr -= clock.delta_time
        if self.casting_cdr < 0:
            # case 1 fulfilled, begin alert state
            # print("attacking")
            self.handler.set_active_state(MAGE_POSTCAST_STATE)

class PostcastState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_POSTCAST_STATE, parent)
        self.cani = MAGE_POSTCAST_ANIM
        self.wparticle = False

    def start(self):
        self.cani = MAGE_POSTCAST_ANIM
        self.wparticle = False
        self.parent.aregist[MAGE_POSTCAST_ANIM].fini = 0
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, self.cani)

        # case 1: finish postcast
        if not self.parent.phandler.ap_count:
            self.wparticle = True
        if self.parent.aregist[MAGE_POSTCAST_ANIM].fini > 0:
            if self.wparticle:
                # case 1 fulfilled, begin alrt
                # add finished spell to world
                skill = self.parent.skhandler.get_skill(fireball.SKILL_NAME)
                fire = skill.activate(self.parent, self.parent.atk_phandler)
                self.parent.add_active_attack(fire)
                fire.position = maths.convert_array_to_int(self.parent.rect.center)
                fire.motion = self.parent.player_dis.normalize() * 2
                scenehandler.SceneHandler.CURRENT.handler.add_entity(fire)
                self.handler.set_active_state(MAGE_ALERT_STATE)
        # case 2: interrupted -> backlash 

class FlightState(state.EntityState):
    def __init__(self, parent):
        super().__init__(MAGE_FLIGHT_STATE, parent)

    def distance_desire_coef(self, dis: float) -> float:
        return 1/(.05*dis + 4/5)

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, MAGE_RUN_ANIM)
        # player is already known to be nearby
        if self.parent.player_dis:
            self.parent.player_dis.normalize()
        self.parent.motion.xy -= self.parent.player_dis.xy * clock.delta_time * self.distance_desire_coef(self.handler.player_dis)
        if self.handler.player_dis > MAGE_PREFERED_DISTANCE:
            self.handler.current_state = MAGE_ALERT_STATE

        # case 1: player is too close --> go to melee def/atk mode
        if self.handler.player_dis < MAGE_CRITICAL_DEF_DISTANCE:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(MAGE_PRECAST_STATE)
        # case 2: player leaves zone
        elif self.handler.player_dis > MAGE_PREFERED_DISTANCE:
            # case 2 fulfilled, begin alert state
            self.handler.set_active_state(MAGE_ALERT_STATE)

class StateHandler(statehandler.StateHandler):
    def __init__(self, mage):
        super().__init__(MAGE_IDLE_STATE)
        self.mage = mage
        self.player_dis = 0

        # add all necassary states
        self.add_state(IdleState(self.mage))
        self.add_state(AlertState(self.mage))
        self.add_state(PrecastState(self.mage))
        self.add_state(CastingState(self.mage))
        self.add_state(FlightState(self.mage))
        self.add_state(PostcastState(self.mage))

# ------------- mage particle system ------------ #

def particle_create(self):
    self.p_count += 1
    # calculate x and y
    theta = maths.normalized_random() * 3.14
    x = maths.math.sin(theta)*MAGE_PARTICLE_SPAWN_RADIUS + self.parent.rel_hitbox.centerx
    y = maths.math.cos(theta)*MAGE_PARTICLE_SPAWN_RADIUS + self.parent.rel_hitbox.centery
    mx = maths.math.sin(theta+3.14/2)
    my = maths.math.cos(theta+3.14/2)
    self.particles[self.p_count] = [self.p_count, x, y, 1, self.start_life, mx, my]

def particle_update(self, p, surface):
    p[PARTICLE_LIFE] -= clock.delta_time
    if p[PARTICLE_LIFE] < 0:
        self.rq.append(p[PARTICLE_ID])
        return
    # update position
    p[PARTICLE_MX] *= PLERP_COEF
    p[PARTICLE_MY] *= PLERP_COEF
    off = pygame.math.Vector2(self.parent.rel_hitbox.centerx - p[PARTICLE_X], self.parent.rel_hitbox.centery - p[PARTICLE_Y])
    off.normalize_ip()
    p[PARTICLE_MX] += off.x * clock.delta_time
    p[PARTICLE_MY] += off.y * clock.delta_time

    p[PARTICLE_X] += p[PARTICLE_MX]
    p[PARTICLE_Y] += p[PARTICLE_MY]
    # render
    pygame.draw.circle(surface, self.color, (p[PARTICLE_X], p[PARTICLE_Y]), 1)


class ParticleHandler(particle.ParticleHandler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_color(MAGE_PARTICLE_COLOR)
        self.set_freq(1/MAGE_PARTICLE_FREQ)
        self.set_life(MAGE_PARTICLE_LIFE)
        self.set_create_func(particle_create)
        self.set_update_func(particle_update)

# -------- mage class ------------------- #

class Mage(entityext.GameEntity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__(ENTITY_NAME, MAGE_HEALTH, MAGE_MANA)
        self.aregist = Mage.ANIM_CATEGORY.create_registry_for_all()
        self.sprite = self.aregist[MAGE_IDLE_ANIM].get_frame()
        self.hitbox = self.aregist[MAGE_IDLE_ANIM].get_hitbox()
        # distance from player
        self.player_dis = pygame.math.Vector2()
        
        # state handler
        self.shandler = StateHandler(self)
        # particle handlers
        self.phandler = ParticleHandler(self)
        self.atk_phandler = fireball.FireParticleHandler(self)
        # skill tree
        self.skhandler = MAGE_SKILL_TREE.get_registry(self)

    def update(self):
        self.player_dis.x = singleton.PLAYER.rect.centerx - self.rect.centerx
        self.player_dis.y = singleton.PLAYER.rect.centery - self.rect.centery
        self.shandler.player_dis = self.player_dis.magnitude()

        self.shandler.update()
        scenehandler.SceneHandler.CURRENT.world.move_entity(self)

        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, 1, 0), self.rect)
        # entity.render_entity_hitbox(self, surface)
        pygame.draw.circle(surface, (255, 0, 0), self.rel_hitbox.center, MAGE_DETECT_RADIUS, width=1)
        pygame.draw.circle(surface, (0, 0, 255), self.rel_hitbox.center, MAGE_PREFERED_DISTANCE, width=1)
        pygame.draw.circle(surface, (0, 100, 100), self.rel_hitbox.center, MAGE_CRITICAL_DEF_DISTANCE, width=1)
        # particle handler
        self.phandler.render(surface)
        self.atk_phandler.render(surface)

# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/mage.json")
Mage.ANIM_CATEGORY = animation.Category.get_category(MAGE_ANIM_CAT)
Mage.ANIM_CATEGORY.apply_func_to_animations(animationext.handle_handle_position)


