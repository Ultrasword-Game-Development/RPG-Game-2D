import pygame
from engine import entity, clock, maths
from engine import animation, user_input

PLAYER_ANIM_CAT = "player"

PLAYER_IDLE_ANIM = "idle"
PLAYER_RUN_ANIM = "run"

MOVE_SPEED = 30
LERP_COEF = 0.3

class Player(entity.Entity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__()
        self.aregist = Player.ANIM_CATEGORY.get_animation(PLAYER_IDLE_ANIM).get_registry()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.rect.x += self.hitbox.x
        self.rect.y += self.hitbox.y
    
    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.rect.x -= self.hitbox.x
        self.rect.y -= self.hitbox.y
        self.hitbox = self.aregist.get_hitbox()
        self.rect.w, self.rect.h = self.hitbox.w, self.hitbox.h
        self.rect.x += self.hitbox.x
        self.rect.y += self.hitbox.y
        # movement
        if user_input.is_key_pressed(pygame.K_d):
            self.motion.x += MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_a):
            self.motion.x -= MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_w):
            self.motion.y -= MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_s):
            self.motion.y += MOVE_SPEED * clock.delta_time
        self.motion.x = maths.lerp(self.motion.x, 0.0, LERP_COEF)
        self.motion.y = maths.lerp(self.motion.y, 0.0, LERP_COEF)

        self.rect.x += round(self.motion.x)
        self.rect.y += round(self.motion.y)

    def render(self, window):
        window.blit(self.sprite, self.rect)
        entity.render_entity_hitbox(self, window)


# ------------ setup ----------- #
animation.load_and_parse_aseprite_animation("assets/sprites/player.json")
Player.ANIM_CATEGORY = animation.Category.get_category(PLAYER_ANIM_CAT)
    

