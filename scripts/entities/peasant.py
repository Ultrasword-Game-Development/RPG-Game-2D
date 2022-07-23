import pygame

from engine import statehandler, animation, clock

from scripts import singleton, entityext, skillext, animationext
from scripts.game import state, skillhandler
from scripts.entities import fireball


# ---------- CONST VALUES ---------

ENTITY_NAME = "PEASANT"
_HEALTH = 100
_MANA = 100

LERP_COEF = 0.3

DETECT_RANGE = 80
ATTACK_RANGE = 30
MOVE_SPEED = 20

ALERT_DECISION_PAUSE = 0.5
IDLE_MOVE_PAUSE = 3.0

IDLE_MOVE_DECISION = 1.4
IDLE_MOVE_WAIT = 1.0

# -------- animations ------------

ANIM_CAT = "peasant"
IDLE_ANIM = "idle"
RUN_ANIM = "run"

IDLE_STATE = "idle"
ALERT_STATE = "alert"
APPROACH_STATE = "approach"

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
        self.decision_timer = clock.Timer(IDLE_MOVE_PAUSE)
        self.pause_timer = clock.Timer(IDLE_MOVE_WAIT)
        self.c_ani = IDLE_ANIM

    def start(self):
        self.parent.aregist[IDLE_ANIM].f_num = 0
        self.decision_timer.st = 0
        self.pause_timer.st = 0
        self.c_ani = IDLE_ANIM
    
    def update(self):
        entityext.update_ani_and_hitbox(self.parent, self.c_ani)
        # case 1: entity comes into range
        if self.handler.player_dis < DETECT_RANGE:
            # case 1 fulfilled:
            self.handler.set_active_state(ALERT_STATE)
            return
        # print(self.decision_timer.st, self.pause_timer.st)

        self.decision_timer.update()
        if self.decision_timer.changed:
            self.decision_timer.changed = False
            print("decision time")

        self.pause_timer.update()
        if self.pause_timer.changed:
            self.pause_timer.changed = False
            print("pause done")

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
        self.parent.motion += self.parent.player_dis.normalize() * clock.delta_time * MOVE_SPEED
        # case 1: player leaves range
        if self.handler.player_dis > DETECT_RANGE:
            # case 1 fulfilled
            self.handler.set_active_state(ALERT_STATE)


class StateHandler(statehandler.StateHandler):
    def __init__(self, peasant):
        super().__init__(IDLE_STATE)
        self.peasant = peasant
        self.player_dis = 0
        
        # add all states
        self.add_state(IdleState(self.peasant))
        self.add_state(AlertState(self.peasant))
        self.add_state(ApproachState(self.peasant))
        self.add_state(IdleMoveState(self.peasant))


# --------------- peasant class -------------- #


class Peasant(entityext.GameEntity):
    ANIM_CATEGORY = None

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

        self.rect.x += round(self.motion.x)
        self.rect.y += round(self.motion.y)
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, 1, 0), self.rect)
        pygame.draw.circle(surface, (0,255,0), self.rel_hitbox.center, DETECT_RANGE, 1)

# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/peasant.json")
Peasant.ANIM_CATEGORY = animation.Category.get_category(ANIM_CAT)
Peasant.ANIM_CATEGORY.apply_func_to_animations(animationext.handle_handle_position)

