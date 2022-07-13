import pygame
from engine import entity, clock, maths
from engine import animation, user_input
from engine import statehandler

from scripts import singleton


MAGE_ANIM_CAT = "mage"
MAGE_IDLE_ANIM = "idle"
MAGE_RUN_ANIM = "run"

MAGE_IDLE_STATE = "idle"
MAGE_FLIGHT_STATE = "flight"
MAGE_FIGHT_STATE = "fight"

MOVE_SPEED = 20
LERP_COEF = 0.3

MAGE_DETECT_RADIUS = 100
MAGE_PREFERED_DISTANCE = 80

MAGE_IDLE_ANIM_i = 0
MAGE_RUN_ANIM_i = 1


# --------- mage state handler ---------- #

def mage_state_manager(self):
    dis = self.handler_data['pdis']
    if dis > 100:
        return MAGE_IDLE_STATE
    if dis < 80:
        return MAGE_FLIGHT_STATE
    return MAGE_FIGHT_STATE


class MageIdleState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_IDLE_STATE)
        self.parent = parent

    def update(self):
        self.parent.aregist[MAGE_IDLE_ANIM_i].update()
        self.parent.sprite = self.parent.aregist[MAGE_IDLE_ANIM_i].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_IDLE_ANIM_i].get_hitbox()
        self.parent.calculate_rel_hitbox()


class MageFlightState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_FLIGHT_STATE)
        self.parent = parent

    def distance_desire_coef(self, dis: float) -> float:
        return 1/(.05*dis + 4/5)

    def update(self):
        self.parent.aregist[MAGE_IDLE_ANIM_i].update()
        self.parent.sprite = self.parent.aregist[MAGE_IDLE_ANIM_i].get_frame()
        self.parent.hitbox = self.parent.aregist[MAGE_IDLE_ANIM_i].get_hitbox()
        self.parent.calculate_rel_hitbox()
        # player is alreayd known to be nearby
        if self.parent.player_dis:
            self.parent.player_dis.normalize()
        self.parent.motion.xy -= self.parent.player_dis.xy * clock.delta_time * self.distance_desire_coef(self.handler.handler_data['pdis'])


class MageFightState(statehandler.State):
    def __init__(self, parent):
        super().__init__(MAGE_FIGHT_STATE)
        self.parent = parent
    
    def update(self):
        pass

# -------- mage class ------------------- #

class Mage(entity.Entity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__()
        self.aregist = (Mage.ANIM_CATEGORY.get_animation(MAGE_IDLE_ANIM).get_registry(), Mage.ANIM_CATEGORY.get_animation(MAGE_RUN_ANIM).get_registry())
        self.sprite = self.aregist[0].get_frame()
        self.hitbox = self.aregist[0].get_hitbox()
        # distance from player
        self.player_dis = pygame.math.Vector2()
        
        # state handler
        self.shandler = statehandler.StateHandler()
        self.shandler.set_data("parent", self)
        self.shandler.set_management_func(mage_state_manager)

        self.shandler.add_state(MageIdleState(self))
        self.shandler.add_state(MageFlightState(self))
        self.shandler.add_state(MageFightState(self))
    
    def update(self):
        self.player_dis.x = singleton.PLAYER.rect.x - self.rect.x
        self.player_dis.y = singleton.PLAYER.rect.y - self.rect.y
        self.shandler.set_data("pdis", self.player_dis.magnitude())

        self.shandler.update()

        self.rect.x += round(self.motion.x)
        self.rect.y += round(self.motion.y)
        self.motion *= LERP_COEF

    def render(self, surface):
        surface.blit(self.sprite, self.rect)
        entity.render_entity_hitbox(self, surface)
        pygame.draw.circle(surface, (255, 0, 0), self.rel_hitbox.center, 100, width=1)
        pygame.draw.circle(surface, (0, 0, 255), self.rel_hitbox.center, 80, width=1)

# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/mage.json")
Mage.ANIM_CATEGORY = animation.Category.get_category(MAGE_ANIM_CAT)
