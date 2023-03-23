import pygame
import soragl as SORA
import struct

from pygame import draw as pgdraw
from pygame import math as pgmath

from soragl import animation, scene, physics, base_objects, mgl, smath, signal

# ------------------------------ #
# setup

WW = 1280
WINDOW_SIZE = [WW, int(WW / 16 * 9)]
WW = 1280 // 3
FB_SIZE = [WW, int(WW / 16 * 9)]

# mac version -- since no opengl
SORA.initialize(
    {
        "fps": 60,
        "window_size": WINDOW_SIZE,
        "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF,
        "window_bits": 32,
        "framebuffer_flags": pygame.SRCALPHA,
        "framebuffer_size": FB_SIZE,
        "framebuffer_bits": 32,
        "debug": True,
    }
)

SORA.create_context()

# ------------------------------- #
# imports

from scripts import singleton

from scripts.entities import player, mage, peasant, test
from scripts.entities import particle_scripts
from scripts.environment import grass, ambient, wind

# ------------------------------- #

sc = scene.Scene(config=scene.load_config(scene.Scene.DEFAULT_CONFIG))
scw = sc.make_layer(sc.get_config(), 1)
# scw.get_chunk(0, 0)
BG_COL = (153, 220, 80)

# -- add entities
ph = scw.add_entity(particlescripts.ParticleHandler(None))
ph.rect.topleft = (100, 100)
ph.color = (255, 0, 0)
ph.set_freq(1 / 15)
ph.set_life(3)
ph.create_func = particle_scripts.GRAVITY_PARTICLE_CREATE
ph.update_func = particle_scripts.GRAVITY_PARTICLE_UPDATE





# aspects
# scw.add_aspect(base_objects.TileMapDebug())
scw.add_aspect(base_objects.SpriteRendererAspect())
scw.add_aspect(base_objects.Collision2DRendererAspectDebug())
scw.add_aspect(base_objects.Area2DAspect())
scw.add_aspect(base_objects.RenderableAspect())

# push scene
scene.SceneHandler.push_scene(sc)

# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    # SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # SORA.FRAMEBUFFER.fill((0, 0, 0, 255))
    SORA.FRAMEBUFFER.fill(BG_COL)
    SORA.DEBUGBUFFER.fill((0, 0, 0, 0))
    # pygame update + render
    scene.SceneHandler.update()

    if SORA.is_key_clicked(pygame.K_d) and SORA.is_key_pressed(pygame.K_LSHIFT):
        SORA.DEBUG = not SORA.DEBUG
    if SORA.is_mouse_clicked(0):
        # add a ball object
        b = ball.Ball(smath.randint(5, 20))
        b.position.xy = SORA.get_mouse_rel()
        scw.add_entity(b)
    
    # update signals
    signal.handle_signals()
    # push frame
    SORA.push_framebuffer()
    # pygame.display.flip()
    # update events
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock tick
    SORA.CLOCK.tick(SORA.FPS)
    SORA.update_time()

pygame.quit()
