# -------------------------------------------------- #
# imports
import pygame
from engine.gamesystem.entity import EntityTypes
from engine.graphics import animation
from engine.misc import maths, user_input, clock

from engine.handler.eventhandler import Event, Eventhandler

from scripts import entityext, animationext, singleton

# -------------------------------------------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/player.json")


# -------------------------------------------------- #


class Player(entityext.GameEntity):
    TYPE = "Player"

    # -------------------------------------------------- #
    # animations
    ANIM_CAT = "player"
    IDLE_ANIM = "idle"
    RUN_ANIM = "run"

    # load
    ANIM_CATEGORY = animation.Category.get_category(ANIM_CAT)

    # -------------------------------------------------- #
    # statistics
    MS = 30
    LC = 0.5

    # -------------------------------------------------- #
    # signals
    MOVEMENT_SIGNAL = "player-move"

    # wrappers
    MOVEMENT_WRAPPER = Eventhandler.register_to_signal(MOVEMENT_SIGNAL,
                                                       lambda x: print(x.name, f"{x.data['x']:.2f}, {x.data['y']:.2f}"))

    # -------------------------------------------------- #
    # buffered objects
    MOVE_EVENT = Event(MOVEMENT_SIGNAL, {'x': 0, 'y': 0})

    # -------------------------------------------------- #

    def __init__(self):
        # mana will change in future
        super().__init__("Player", 100, 100)
        self.aregist = Player.ANIM_CATEGORY.create_registry_for_all()
        self.sprite = self.aregist[Player.IDLE_ANIM].get_frame()
        self.hitbox = self.aregist[Player.IDLE_ANIM].get_hitbox()
        # camera and events
        self.camera = None
        self.priority = True

    def start(self):
        # grab camera from layer
        self.camera = self.layer.camera
        self.camera.set_target(self)
        # tell camera to calculate motion
        self.camera.track_target()

    def update(self):
        # animations - etc
        entityext.update_ani_and_hitbox(self, Player.IDLE_ANIM, handle=False)
        # smooth motion
        self.motion = maths.lerp(self.motion, singleton.ZERO, Player.LC)

        # movement
        if user_input.is_key_pressed(pygame.K_d):
            self.motion.x += Player.MS * clock.delta_time
        if user_input.is_key_pressed(pygame.K_a):
            self.motion.x -= Player.MS * clock.delta_time
        if user_input.is_key_pressed(pygame.K_w):
            self.motion.y -= Player.MS * clock.delta_time
        if user_input.is_key_pressed(pygame.K_s):
            self.motion.y += Player.MS * clock.delta_time

        if user_input.is_key_pressed(pygame.K_k):
            self.kill()

        # project movement to world
        self.layer.world.move_entity(self)
        self.move_to_position()
        # update camera
        self.camera.campos -= self.motion
        self.camera.track_target()
        self.camera.update()

        # event testing
        # Player.MOVE_EVENT.data['x'] = self.motion.x
        # Player.MOVE_EVENT.data['y'] = self.motion.y
        # self.eventhandler.emit_signal(Player.MOVE_EVENT)

    def render(self, surface):
        # surface.blit(self.sprite, self.get_glob_pos())
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, True, False),
                     self.camera.get_target_rel_pos())

    def debug(self, surface):
        super().debug(surface)

    def kill(self):
        super().kill()


# -------------------------------------------------- #
# setup
EntityTypes.register_entity_type(Player.TYPE, Player)
