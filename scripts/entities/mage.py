import pygame
from engine import entity, clock, maths
from engine import animation, user_input


MAGE_ANIM_CAT = "mage"

MAGE_IDLE_ANIM = "idle"
MAGE_RUN_ANIM = "run"

MOVE_SPEED = 20
LERP_COEF = 0.3

class Mage(entity.Entity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__()
        self.aregist = Mage.ANIM_CATEGORY.get_animation(MAGE_IDLE_ANIM).get_registry()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
    
    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        # movement

        self.rect.x += round(self.motion.x)
        self.rect.y += round(self.motion.y)
    
    def render(self, surface):
        surface.blit(self.sprite, self.rect)
        entity.render_entity_hitbox(self, surface)


# ----------- setup -------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/mage.json")
Mage.ANIM_CATEGORY = animation.Category.get_category(MAGE_ANIM_CAT)
