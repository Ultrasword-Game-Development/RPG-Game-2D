# -------------------------------------------------- #
# imports

import engine

from engine.handler import scenehandler
from engine.handler.eventhandler import Eventhandler
from engine.misc import clock, user_input, maths
from engine.handler.filehandler import *

from engine.gamesystem import particle
from engine.window import Window

from engine import singleton as EGLOB

# -------------------------------------------------- #
# engine initialization

WINDOW_CAPTION = "Default Title"
WW = 1280
WINDOW_SIZE = [WW, int(WW/16*9)]
WW = 1280//3
FB_SIZE = [WW, int(WW/16*9)]

FPS = 60

Window.create_window(WINDOW_CAPTION, WINDOW_SIZE[0], WINDOW_SIZE[1], pygame.RESIZABLE | pygame.DOUBLEBUF , 16)
# window.set_icon()
fb = Window.create_framebuffer(FB_SIZE[0], FB_SIZE[1], flags=0, bits=32).convert_alpha()

# -------------------------------------------------- #
# ! CHANGE THESE IF YOU WANT !
EGLOB.DEBUG = False
EGLOB.RENDER_DIS = [3, 2]

background = (255, 255, 255)

# -------------------------------------------------- #
# external imports


# -------------------------------------------------- #
# default initializing world

__scene = scenehandler.Scene()
scenehandler.SceneHandler.push_state(__scene)
__layer = __scene.add_layer()
_HANDLER = __layer.handler
_WORLD = __layer.world

# -------------------------------------------------- #
# object initialization


# -------------------------------------------------- #

_HANDLER.handle_changes()
clock.start()
while Window.running:
    # -------------------------------------------------- #
    # update current scene
    if scenehandler.SceneHandler.CURRENT:
        fb.fill(background)
        # update and render
        scenehandler.SceneHandler.CURRENT.update(fb)

    # eventhandler updates
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

    pygame.display.update()
    clock.update()

# -------------------------------------------------- #
# close engine
engine.end()

