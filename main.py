import pygame

from engine.globals import *

from engine import clock, user_input, handler, animation
from engine import particle, world, chunk, tile

from engine.window import Window
from engine.filehandler import *

WINDOW_CAPTION = "RPG Game"
WW = 1280
WINDOW_SIZE = [WW, int(WW/16*9)]
WW//=3
FB_SIZE = [WW, int(WW/16*9)]

FPS = 60

Window.create_window(WINDOW_CAPTION, WINDOW_SIZE[0], WINDOW_SIZE[1], pygame.RESIZABLE, 16)
# window.set_icon()
fb = pygame.Surface(FB_SIZE, 0, 32).convert_alpha()


# -------- external imports --------- #

from scripts.entities import player, particle_scripts

# ----------------------------------- #

STATE = handler.Handler()


ph = particle.ParticleHandler()
ph.rect.topleft = (100, 100)
ph.color = (255, 0, 0)
ph.set_freq(1/15)
ph.set_life(3)
ph.create_func = particle_scripts.GRAVITY_PARTICLE_CREATE
ph.update_func = particle_scripts.GRAVITY_PARTICLE_UPDATE

p = player.Player()

ph.data['player'] = p

STATE.add_entity(p)
# STATE.add_entity(ph)

green_block = pygame.Surface((16,16), 0, 32)
green_block.fill((0, 255, 0))

WORLD = world.World()
chunk = chunk.Chunk(0, 0)
for x in range(TILEMAP_WIDTH):
    chunk.get_tile_at(x, 3).sprite = green_block
WORLD.add_chunk(chunk)

# ----------------------------- #

clock.start()
while Window.running:
    fb.fill((255, 255, 255))
    chunk.render(fb)


    STATE.handle_entities(fb)

    # rescale framebuffer to window
    Window.instance.blit(pygame.transform.scale(fb, (Window.WIDTH, Window.HEIGHT)), (0,0))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            Window.running = False
        elif e.type == pygame.KEYDOWN:
            # keyboard press
            user_input.key_press(e)
        elif e.type == pygame.KEYUP:
            # keyboard release
            user_input.key_release(e)
        elif e.type == pygame.MOUSEMOTION:
            # mouse movement
            user_input.mouse_move_update(e)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            # mouse press
            user_input.mouse_button_press(e)
        elif e.type == pygame.MOUSEBUTTONUP:
            # mouse release
            user_input.mouse_button_release(e)
        elif e.type == pygame.WINDOWRESIZED:
            # window resized
            Window.handle_resize(e)
            fbsize = fb.get_size()
            user_input.update_ratio(Window.WIDTH, Window.HEIGHT, fbsize[0], fbsize[1])
    pygame.display.flip()
    clock.update()


pygame.quit()

