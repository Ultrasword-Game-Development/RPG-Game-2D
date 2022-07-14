import pygame
from engine import entity, clock, maths
from engine import animation, user_input
from engine import statehandler, particle

from scripts import singleton



# ---------- CONST VALUES ---------

# -------- animations ------------
MAGE_ANIM_CAT = "mage"
MAGE_IDLE_ANIM = "idle"
MAGE_RUN_ANIM = "run"
MAGE_PRECAST_ANIM = "pre_attack"
MAGE_CASTING_ANIM = "casting"

# --------- states ---------------

MAGE_IDLE_STATE = "idle"
MAGE_ALERT_STATE = "alert"
MAGE_FLIGHT_STATE = "flight"
MAGE_PRECAST_STATE = "precast"
MAGE_CASTING_STATE = "casting"
MAGE_ATTACK_STATE = "firing"

# --------------------------------

MOVE_SPEED = 20
LERP_COEF = 0.3

MAGE_DETECT_RADIUS = 130
MAGE_PREFERED_DISTANCE = 70
MAGE_CRITICAL_DEF_DISTANCE = 30

# ---------- CDR TIMES ------------
MAGE_ALERT_PRECAST_CDR = 1.0
MAGE_PRECAST_CDR = 0.4
MAGE_DEFAULT_CASTING_CDR = 1.0


# TODO:
# 1. create new entity object (specific to this game)
# 2. create enw State object (specific to this game /  made for entities + player)

# --------- mage state handler ---------- #

class MageIdleState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_IDLE_STATE)
        self.parent = parent

    def update(self):
        self.parent.aregist[MAGE_IDLE_ANIM].update()
        self.parent.sprite = self.parent.aregist[MAGE_IDLE_ANIM].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_IDLE_ANIM].get_hitbox()
        self.parent.calculate_rel_hitbox()
        # check for player distance etc
        if self.handler.player_dis < MAGE_DETECT_RADIUS:
            self.handler.set_active_state(MAGE_ALERT_STATE)
        # also calculate for idle movement


class MageAlertState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_ALERT_STATE)
        self.parent = parent
        self.countdown = MAGE_ALERT_PRECAST_CDR

    def start(self):
        print("alert")
        self.countdown = MAGE_ALERT_PRECAST_CDR

    def update(self):
        self.parent.aregist[MAGE_IDLE_ANIM].update()
        self.parent.sprite = self.parent.aregist[MAGE_IDLE_ANIM].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_IDLE_ANIM].get_hitbox()
        self.parent.calculate_rel_hitbox()
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


class MagePrecastState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_PRECAST_STATE)
        self.parent = parent
        self.precast_cdr = MAGE_PRECAST_CDR
    
    def start(self):
        print("starting precast")
        self.precast_cdr = MAGE_PRECAST_CDR
        self.parent.aregist[MAGE_PRECAST_ANIM].fini = 0
    
    def update(self):
        self.parent.aregist[MAGE_PRECAST_ANIM].update()
        self.parent.sprite = self.parent.aregist[MAGE_PRECAST_ANIM].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_PRECAST_ANIM].get_hitbox()
        self.parent.calculate_rel_hitbox()
        # case 1: finish precast
        if self.parent.aregist[MAGE_PRECAST_ANIM].fini > 0:
            # case 1 fulfilled, begin casting
            self.handler.set_active_state(MAGE_CASTING_STATE)


class MageCastingState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_CASTING_STATE)
        self.parent = parent
        self.casting_cdr = MAGE_DEFAULT_CASTING_CDR
    
    def start(self):
        print("casting spell")
        self.casting_cdr = MAGE_ALERT_PRECAST_CDR
        # decide on an attack and set casting_cdr depending on attack
    
    def update(self):
        self.parent.aregist[MAGE_CASTING_ANIM].update()
        self.parent.sprite = self.parent.aregist[MAGE_CASTING_ANIM].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_CASTING_ANIM].get_hitbox()
        self.parent.calculate_rel_hitbox()
        # case 1: finish casting
        self.casting_cdr -= clock.delta_time
        if self.casting_cdr < 0:
            # case 1 fulfilled, begin alert state
            print("attacking")
            self.handler.set_active_state(MAGE_ALERT_STATE)


class MageFlightState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_FLIGHT_STATE)
        self.parent = parent

    def distance_desire_coef(self, dis: float) -> float:
        return 1/(.05*dis + 4/5)

    def update(self):
        self.parent.aregist[MAGE_IDLE_ANIM].update()
        self.parent.sprite = self.parent.aregist[MAGE_IDLE_ANIM].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_IDLE_ANIM].get_hitbox()
        self.parent.calculate_rel_hitbox()
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




class MageStateHandler(statehandler.StateHandler):
    def __init__(self, mage):
        super().__init__(MAGE_IDLE_STATE)
        self.mage = mage
        self.player_dis = 0
        self.start_cast = False
        self.is_casting = False
        self.attacking = False

        # add all necassary states
        self.add_state(MageIdleState(self.mage))
        self.add_state(MageAlertState(self.mage))
        self.add_state(MagePrecastState(self.mage))
        self.add_state(MageCastingState(self.mage))
        self.add_state(MageFlightState(self.mage))


# -------- mage class ------------------- #

class Mage(entity.Entity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__()
        self.aregist = Mage.ANIM_CATEGORY.create_registry_for_all()
        self.sprite = self.aregist[MAGE_IDLE_ANIM].get_frame()
        self.hitbox = self.aregist[MAGE_IDLE_ANIM].get_hitbox()
        # distance from player
        self.player_dis = pygame.math.Vector2()
        
        # state handler
        self.shandler = MageStateHandler(self)
    
    def update(self):
        self.player_dis.x = singleton.PLAYER.rect.x - self.rect.x
        self.player_dis.y = singleton.PLAYER.rect.y - self.rect.y
        self.shandler.player_dis = self.player_dis.magnitude()

        self.shandler.update()

        self.rect.x += round(self.motion.x)
        self.rect.y += round(self.motion.y)
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite, self.rect)
        # entity.render_entity_hitbox(self, surface)
        pygame.draw.circle(surface, (255, 0, 0), self.rel_hitbox.center, MAGE_DETECT_RADIUS, width=1)
        pygame.draw.circle(surface, (0, 0, 255), self.rel_hitbox.center, MAGE_PREFERED_DISTANCE, width=1)
        pygame.draw.circle(surface, (0, 100, 100), self.rel_hitbox.center, MAGE_CRITICAL_DEF_DISTANCE, width=1)

# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/mage.json")
Mage.ANIM_CATEGORY = animation.Category.get_category(MAGE_ANIM_CAT)
