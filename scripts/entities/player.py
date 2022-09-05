import pygame

from engine.misc import clock, maths, user_input
from engine.handler import scenehandler
from engine.graphics import animation, camera

from engine import singleton as EGLOB

from scripts import entityext, singleton

ENTITY_NAME = "Player"
PLAYER_HEALTH = 100
PLAYER_MANA = 100


PLAYER_ANIM_CAT = "player"
PLAYER_IDLE_ANIM = "idle"
PLAYER_RUN_ANIM = "run"

MOVE_SPEED = 30
LERP_COEF = 0.5


class Player(entityext.GameEntity):
    ANIM_CATEGORY = None

    def __init__(self):
        super().__init__(ENTITY_NAME, PLAYER_HEALTH, PLAYER_MANA)
        self.aregist = Player.ANIM_CATEGORY.get_animation(PLAYER_IDLE_ANIM).get_registry()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()

        self.camera = camera.Camera()
        self.camera.set_target(self)
        self.camera.track_target()
    
    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.motion.x = maths.lerp(self.motion.x, 0.0, LERP_COEF)
        self.motion.y = maths.lerp(self.motion.y, 0.0, LERP_COEF)
        # movement
        if user_input.is_key_pressed(pygame.K_d):
            self.motion.x += MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_a):
            self.motion.x -= MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_w):
            self.motion.y -= MOVE_SPEED * clock.delta_time
        if user_input.is_key_pressed(pygame.K_s):
            self.motion.y += MOVE_SPEED * clock.delta_time

        self.layer.world.move_entity(self)
        self.move_to_position()
        # update camera
        self.camera.campos -= self.motion
        self.camera.track_target()
        self.camera.update()

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, True, False), self.camera.get_target_rel_pos())
        # entity.render_entity_hitbox(self, surface)


# ------------ setup ----------- #
animation.load_and_parse_aseprite_animation("assets/sprites/player.json")
Player.ANIM_CATEGORY = animation.Category.get_category(PLAYER_ANIM_CAT)
entityext.EntityTypes.register_entity_type(ENTITY_NAME, Player)