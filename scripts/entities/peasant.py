import pygame

from engine.misc import clock, maths
from engine.handler import statehandler, scenehandler
from engine.graphics import animation
from engine.gamesystem import entity

from scripts import singleton, entityext, skillext, animationext
from scripts.game import state, skillhandler
from scripts.entities import fireball


# trailtest
from scripts.entities import test
from scripts.entities import particle_scripts, attacks


# ---------- CONST VALUES ---------

ENTITY_NAME = "PEASANT"
_HEALTH = 100
_MANA = 100

LERP_COEF = 0.3

DETECT_RANGE = 80
ATTACK_RANGE = 30
MELEE_ATTACK_RANGE = 25
MAGE_HOVER_DIS = 120

MS = 30
IDLE_MS = 39

ENVIRO_CHECK_TIMER = 2.5
ALERT_DECISION_PAUSE = 0.5
IDLE_MOVE_PAUSE = 3.0

IDLE_MOVE_PERIOD = 1.4
IDLE_MOVE_WAIT = 1.0
ORBIT_ATTACK_WAIT = 1.5
RUN_TIME_PERIOD = 1.5

IDLE_MOVE_MAGE_WEIGHT = 0.6

# -------- animations ------------

ANIM_CAT = "peasant"
MELEE_ATTACK_ANIM_CAT = "melee_swing"
MELEE_ATTACK_ANIM = "attack"

IDLE_ANIM = "idle"
RUN_ANIM = "run"

IDLE_STATE = "idle"
ALERT_STATE = "alert"
APPROACH_STATE = "approach"
ORBIT_STATE = "orbit"
ATTACK_STATE = "attack"
RUN_STATE = "run"

IDLE_MOVE_STATE = "idle-move"

# --------- states ---------------

class IdleState(state.EntityState):
    def __init__(self, parent):
        super().__init__(IDLE_STATE, parent)
        self.idle_move_timer = clock.Timer(IDLE_MOVE_PAUSE)
    
    def start(self):
        self.parent.aregist[IDLE_ANIM].f_num = 0
        self.idle_move_timer.wait_time = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)
        # idle movement
        # case 1: player enters detect range
        if self.handler.player_dis < DETECT_RANGE:
            # case 1 fulfilled
            self.handler.set_active_state(ALERT_STATE)
        self.idle_move_timer.update()
        if self.idle_move_timer.changed:
            self.handler.set_active_state(IDLE_MOVE_STATE)

class IdleMoveState(state.EntityState):
    def __init__(self, parent):
        super().__init__(IDLE_MOVE_STATE, parent)
        self.move_timer = clock.Timer(IDLE_MOVE_PERIOD)
        self.pause_timer = clock.Timer(IDLE_MOVE_WAIT)
        self.c_ani = IDLE_ANIM
        self.is_making_dec = True
        self.move_vec = None

    def start(self):
        self.parent.aregist[IDLE_ANIM].f_num = 0
        self.move_timer.st = 0
        self.pause_timer.st = 0
        self.c_ani = IDLE_ANIM
        self.is_making_dec = True
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, self.c_ani)
        # case 1: entity comes into range
        if self.handler.player_dis < DETECT_RANGE:
            # case 1 fulfilled:
            self.handler.set_active_state(ALERT_STATE)
            return
        # print(self.decision_timer.st, self.pause_timer.st)
        # print(self.parent.motion)
        
        # if we are not making a decision, we can start moving the entity
        if not self.is_making_dec:
            # entity is deciding where to move
            self.move_timer.update()
            # add motion to entity
            self.parent.motion += self.move_vec * clock.delta_time
            # check if time is over
            if self.move_timer.changed:
                self.move_timer.changed = False
                self.is_making_dec = True
        else:
            # pause 
            self.pause_timer.update()
            if self.pause_timer.changed:
                # when pausing time is over, we stop making the decision
                self.pause_timer.changed = False
                self.is_making_dec = False
                # TODO - CHANGE TO DETECTING NEARBY MAGES
                if not self.handler.nearby_mage:
                    self.handler.nearby_mage.x = 0.1
                self.move_vec = entityext.find_idle_mot(MS)
                if self.handler.nearby_mage:
                    self.move_vec += self.handler.nearby_mage.normalize() * clock.delta_time * MS * 1.3

class AlertState(state.EntityState):
    def __init__(self, parent):
        super().__init__(ALERT_STATE, parent)
        self.pause = clock.Timer(ALERT_DECISION_PAUSE)
    
    def start(self):
        self.parent.aregist[RUN_ANIM].f_num = 0
        self.pause.wait_time = 0
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)
        self.pause.update()
        if self.pause.changed:
            # case 1 player enters range
            if self.handler.player_dis < DETECT_RANGE:
                # case 1 fulfilled - player detected
                self.handler.set_active_state(APPROACH_STATE)
            # case 2 player leaves detect range
            elif self.handler.player_dis > DETECT_RANGE:
                # case 2 fulfilled - player leaves detected range
                self.handler.set_active_state(IDLE_STATE)

class ApproachState(state.EntityState):
    def __init__(self, parent):
        super().__init__(APPROACH_STATE, parent)
    
    def start(self):
        pass
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, RUN_ANIM)
        # move towards player
        if self.parent.player_dis:
            self.parent.motion += self.parent.player_dis.normalize() * clock.delta_time * MS
        # case 1: player leaves range
        if self.handler.player_dis > DETECT_RANGE:
            # case 1 fulfilled
            self.handler.set_active_state(ALERT_STATE)
        # case 2: player enters orbit range
        elif self.handler.player_dis < ATTACK_RANGE:
            # case 2 fulfilled
            self.handler.set_active_state(ORBIT_STATE)
        # case 3: peasant leaves mage 
        elif self.handler.nearby_mage.magnitude() > MAGE_HOVER_DIS:
            # case 3 fulfilled
            self.handler.set_active_state(RUN_STATE)

class OrbitState(state.EntityState):
    def __init__(self, parent):
        super().__init__(ORBIT_STATE, parent)
        self.attack_timer = clock.Timer(ORBIT_ATTACK_WAIT)

    def start(self):
        self.attack_timer.st = 0
        self.runmode = -1 if maths.np.random.randint(0,2) else 1

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)
        # move to stay in certain range
        rot_vec = self.parent.player_dis.normalize().rotate(90*self.runmode)
        self.parent.motion += rot_vec * MS * clock.delta_time
        for pea in self.handler.nearby_peasants:
            self.parent.motion -= self.parent.distance_to_other(pea).normalize().rotate(10) * MS * clock.delta_time * self.handler.peasant_avoid_weight / 2
        # attack timer update
        self.attack_timer.update()
        # case 1: timer is up
        if self.attack_timer.changed:
            # case 1 fulfilled
            self.attack_timer.changed = False
            self.handler.set_active_state(ATTACK_STATE)

class AttackState(state.EntityState):
    def __init__(self, parent):
        super().__init__(ATTACK_STATE, parent)
    
    def start(self):
        pass

    def update(self):
        # TODO - add new attack animatino in future
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)
        # stop moving
        self.parent.motion *= 0
        # create attack particle
        pos = [self.parent.position.x, self.parent.position.y]
        if self.parent.position.x < singleton.PLAYER.position.x:
            pos[0] = self.parent.rect.w - self.parent.handle_pos[0] + self.parent.position.x
        r = attacks.MeleeStab(pos[0], pos[1], self.parent.MELEE_ATTACK_CATEGORY.get_animation(MELEE_ATTACK_ANIM).get_registry())
        r.motion = self.parent.player_dis.normalize() * 10
        self.parent.layer.handler.add_entity(r)
        # p = test.TrailTest()
        # p.position.xy = self.parent.handle_pos
        # p.position += self.parent.rect.topleft
        # print(p.position, self.parent.rect)
        # scenehandler.SceneHandler.CURRENT.handler.add_entity(p)
        # self.handler.set_active_state(ORBIT_STATE)
        # immediately dip
        self.handler.set_active_state(RUN_STATE)

class RunState(state.EntityState):
    def __init__(self, parent):
        super().__init__(RUN_STATE, parent)
        self.run_timer = clock.Timer(RUN_TIME_PERIOD)
    
    def start(self):
        self.run_timer.st = 0
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, RUN_ANIM)
        # move entity away from player
        self.run_timer.update()
        self.parent.motion += self.handler.nearby_mage.normalize() * MS * clock.delta_time
        for pea in self.handler.nearby_peasants:
            self.parent.motion -= self.parent.distance_to_other(pea).normalize() * MS * clock.delta_time * self.handler.peasant_avoid_weight
        # case 1: run time is over
        if self.run_timer.changed:
            self.run_timer.changed = False
            self.handler.set_active_state(IDLE_STATE)
        # case 2: if player is still too close


class StateHandler(statehandler.StateHandler):
    def __init__(self, peasant):
        super().__init__(IDLE_STATE)
        self.peasant = peasant
        self.player_dis = 0

        # peasants hover around mages
        # this is relative position to the peasant
        self.nearby_mage = pygame.math.Vector2()
        self.search_timer = clock.Timer(ENVIRO_CHECK_TIMER)
        self.search_timer.st = ENVIRO_CHECK_TIMER

        self.nearby_peasants = []
        self.peasant_avoid_weight = 0

        # add all states
        self.add_state(IdleState(self.peasant))
        self.add_state(AlertState(self.peasant))
        self.add_state(ApproachState(self.peasant))
        self.add_state(IdleMoveState(self.peasant))
        self.add_state(OrbitState(self.peasant))
        self.add_state(RunState(self.peasant))
        self.add_state(AttackState(self.peasant))
    
    def update(self):
        super().update()
        self.search_timer.update()
        if self.search_timer.changed:
            self.search_timer.changed = False
            self.nearby_peasants.clear()
            for e in self.peasant.layer.world.find_nearby_entities(self.peasant.p_chunk, 1):
                if type(e) == entity.EntityTypes.get_entity_type("MAGE"):
                    self.nearby_mage = self.peasant.distance_to_other(e)
                elif type(e) == Peasant and e.id != self.peasant.id:
                    self.nearby_peasants.append(e)
            # handle the peasant_avoid_weight
            if self.nearby_peasants:
                self.peasant_avoid_weight = 1/len(self.nearby_peasants)/2
            else: self.peasant_avoid_weight = 0

# --------------- peasant class -------------- #

class Peasant(entityext.GameEntity):
    ANIM_CATEGORY = None
    MELEE_ATTACK_CATEGORY = None

    def __init__(self):
        super().__init__(ENTITY_NAME, _HEALTH, _MANA)
        self.aregist = Peasant.ANIM_CATEGORY.create_registry_for_all()
        self.sprite = self.aregist[IDLE_ANIM].get_frame()
        self.hitbox = self.aregist[IDLE_ANIM].get_hitbox()
        # distance from player
        self.player_dis = pygame.math.Vector2()
        # state handler
        self.shandler = StateHandler(self)
        
    def update(self):
        self.player_dis.x = singleton.PLAYER.rect.centerx - self.rect.centerx
        self.player_dis.y = singleton.PLAYER.rect.centery - self.rect.centery
        self.shandler.player_dis = self.player_dis.magnitude()

        self.shandler.update()

        self.layer.world.move_entity(self)
        self.move_to_position()
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, 1, 0), self.get_glob_pos())
    
    def debug(self, surface):
        super().debug(surface)
        pygame.draw.circle(surface, (0,255,0), self.get_glob_cpos(), DETECT_RANGE, 1)
        pygame.draw.circle(surface, (0, 100, 255), self.get_glob_cpos(), ATTACK_RANGE, 1)

        pygame.draw.line(surface, (255, 0, 0), self.get_glob_cpos(), self.get_glob_cpos() - singleton.UP.rotate(180-self.motion.angle_to(singleton.UP)) * 10)


# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/peasant.json")
animation.load_and_parse_aseprite_animation("assets/sprites/particles/melee_swing.json")
Peasant.ANIM_CATEGORY = animation.Category.get_category(ANIM_CAT)
Peasant.ANIM_CATEGORY.apply_func_to_animations(animationext.handle_handle_position)
Peasant.MELEE_ATTACK_CATEGORY = animation.Category.get_category(MELEE_ATTACK_ANIM_CAT)
print(Peasant.MELEE_ATTACK_CATEGORY)
entity.EntityTypes.register_entity_type(ENTITY_NAME, Peasant)

