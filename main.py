# from OpenGL.GL import *
# from OpenGL.GLU import *
# import numpy as np

from engine.handler import scenehandler
from engine.handler.eventhandler import Eventhandler
from engine.misc import clock, user_input
from engine.handler.filehandler import *

from engine.gamesystem import particle

from engine.window import Window

# --------- initialization -------------- #

WINDOW_CAPTION = "RPG Game"
WW = 1280
WINDOW_SIZE = [WW, int(WW/16*9)]
WW//=3
FB_SIZE = [WW, int(WW/16*9)]

FPS = 60

Window.create_window(WINDOW_CAPTION, WINDOW_SIZE[0], WINDOW_SIZE[1], pygame.RESIZABLE | pygame.DOUBLEBUF , 16)
# window.set_icon()
fb = Window.create_framebuffer(FB_SIZE[0], FB_SIZE[1], flags=0, bits=32).convert_alpha()

# print(singleton.FB_WIDTH)
# -------- external imports --------- #

from scripts import singleton

from scripts.entities import player, mage, peasant, test
from scripts.entities import particle_scripts

# ----------------------------------- #

# CLIENT = client.Client(client.socket.gethostbyname(client.socket.gethostname()))
# CLIENT.connect()


__scene = scenehandler.Scene()
scenehandler.SceneHandler.push_state(__scene)
__layer = __scene.add_layer()
STATE = __layer.handler
WORLD = __layer.world

__scene.add_data("bg_color", (153, 220, 80))


ph = particle.ParticleHandler(None)
ph.rect.topleft = (100, 100)
ph.color = (255, 0, 0)
ph.set_freq(1/15)
ph.set_life(3)
ph.create_func = particle_scripts.GRAVITY_PARTICLE_CREATE
ph.update_func = particle_scripts.GRAVITY_PARTICLE_UPDATE

# tree = entity.Entity()
# tree.sprite = Filehandler.get_image_and_scale_float("assets/environment/tree_leaves1.png", (0.2, 0.2))
# tree.rect = tree.sprite.get_rect()
# trunk = entity.Entity()
# trunk.sprite = Filehandler.get_image_and_scale_float("assets/environment/tree_trunk_base1.png", (0.2, 0.2))
# trunk.rect = trunk.sprite.get_rect()
# trunk.rect.center = (tree.rect.centerx, tree.rect.bottom + trunk.rect.height)

# STATE.add_entity(tree)
# STATE.add_entity(trunk)

singleton.PLAYER = player.Player()
singleton.PLAYER.rect.topleft = (10, 10)

m = mage.Mage()
m.position.xy = (100, 100)

p = peasant.Peasant()
p.position.xy = (200, 200)
p2 = peasant.Peasant()
p2.position.xy = (100, 100)

ph.data['player'] = singleton.PLAYER

# f = fireball.Fire()
# f.rect.topleft = (30, 30)

STATE.add_entity(test.Test())
STATE.add_entity(singleton.PLAYER)
STATE.add_entity(m)
STATE.add_entity(p)
STATE.add_entity(p2)
# STATE.add_entity(f)
# STATE.add_entity(ph)

# -------------------------------------------------- #

clock.start()
while Window.running:
    if scenehandler.SceneHandler.CURRENT:
        fb.fill(scenehandler.SceneHandler.CURRENT.data["bg_color"])
        scenehandler.SceneHandler.CURRENT.update(fb, debug=True)
        # scenehandler.SceneHandler.CURRENT.handler.handle_entities(fb)
        # scenehandler.SceneHandler.CURRENT.handler.debug_handle_entities(fb)
        # scenehandler.SceneHandler.CURRENT.world.handle_chunks(fb)
    Eventhandler.update()

    # rescale framebuffer to window
    Window.instance.blit(pygame.transform.scale(fb, (Window.WIDTH, Window.HEIGHT)), (0,0))

    user_input.update()
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

# CLIENT.close()
pygame.quit()

