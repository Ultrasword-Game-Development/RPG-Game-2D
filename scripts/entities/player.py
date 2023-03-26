# -------------------------------------------------- #
# imports
import pygame

import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

# -------------------------------------------------- #
# animations
ANIM_CAT = "assets/sprites/player.json"
IDLE_ANIM = "idle"
RUN_ANIM = "run"

animation.Category.load_category("assets/sprites/player.json")


# -------------------------------------------------- #
# statistics
MS = 300
LC = 0.1

AREA = (10, 15)

# -------------------------------------------------- #
# signals
MOVEMENT_SIGNAL = signal.register_signal(signal.SignalRegister("player-move"))

# wrappers
MOVEMENT_RECEIVER = MOVEMENT_SIGNAL.add_receiver(
    signal.Receiver(lambda data: print(data))
)

# -------------------------------------------------- #
# player

# TODO -- create game entity for rpg game
class Player(physics.Entity):
    def __init__(self):
        # mana will change in future
        super().__init__()

        # private
        self._current_anim = RUN_ANIM

        # objects
        self.aregist = animation.Category.get_registries_for_all(ANIM_CAT)

        self.c_sprite = base_objects.AnimatedSprite(0, 0, self.aregist[self._current_anim])
        self.c_collision = base_objects.Collision2DComponent()
        # camera and events
        self.camera = None
        self.priority = True

    def on_ready(self):
        self.area = AREA
        self.add_component(self.c_sprite)
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(self.c_collision)
        return
        # TODO - grab camera from layer
        self.camera = self.layer.camera
        self.camera.set_target(self)
        # tell camera to calculate motion
        self.camera.track_target()

    def update(self):
        # TODO -- consider removing
        self.aregist[self._current_anim].update()
        self.velocity = smath.v2lerp(self.velocity, (0, 0), LC)

        # movement
        if SORA.is_key_pressed(pygame.K_d):
            self.velocity.x += MS * SORA.DELTA
        if SORA.is_key_pressed(pygame.K_a):
            self.velocity.x -= MS * SORA.DELTA
        if SORA.is_key_pressed(pygame.K_w):
            self.velocity.y -= MS * SORA.DELTA
        if SORA.is_key_pressed(pygame.K_s):
            self.velocity.y += MS * SORA.DELTA
        if SORA.is_key_pressed(pygame.K_k):
            self.kill()

        # TODO - update camera
        # self.camera.campos -= self.motion
        # self.camera.track_target()
        # self.camera.update()

        # set sprite flipping
        self.c_sprite.flip = self.velocity.x > 0
