import engine
import random

from engine.handler import scenehandler
from engine.handler.eventhandler import Eventhandler
from engine.misc import clock, user_input, maths
from engine.handler.filehandler import *

from engine.gamesystem import particle
from engine.window import Window

from engine import singleton as EGLOB

# --------- initialization -------------- #



WINDOW_CAPTION = "RPG Game"
WW = 1280
WINDOW_SIZE = [WW, int(WW/16*9)]
WW = 1280//3
FB_SIZE = [WW, int(WW/16*9)]

FPS = 60

Window.create_window(WINDOW_CAPTION, WINDOW_SIZE[0], WINDOW_SIZE[1], pygame.RESIZABLE | pygame.DOUBLEBUF , 16)
# window.set_icon()
fb = Window.create_framebuffer(FB_SIZE[0], FB_SIZE[1], flags=0, bits=32).convert_alpha()

# print(singleton.FB_WIDTH)
# -------- external imports --------- #

from oscripts import singleton

from oscripts.entities import player, mage, peasant, test
from oscripts.entities import particle_scripts
from oscripts.environment import grass, ambient, wind

# ----------------------------------- #

# CLIENT = client.Client(client.socket.gethostbyname(client.socket.gethostname()))
# CLIENT.connect()

EGLOB.DEBUG = False
EGLOB.RENDER_DIS = [3, 2]

__scene = scenehandler.Scene()
scenehandler.SceneHandler.push_state(__scene)
__layer = __scene.add_layer()
_HANDLER = __layer.handler
_WORLD = __layer.world

__scene.add_data("bg_color", (153, 220, 80))


ph = particle.ParticleHandler(None)
ph.rect.topleft = (100, 100)
ph.color = (255, 0, 0)
ph.set_freq(1/15)
ph.set_life(3)
ph.create_func = particle_scripts.GRAVITY_PARTICLE_CREATE
ph.update_func = particle_scripts.GRAVITY_PARTICLE_UPDATE

# ----------------------------------- #

singleton.PLAYER = player.Player()
singleton.PLAYER.rect.topleft = (10, 10)

m = mage.Mage()
m.position.xy = (100, 100)

p = peasant.Peasant()
p.position.xy = (120, 120)
p2 = peasant.Peasant()
p2.position.xy = (100, 100)

ph.data['player'] = singleton.PLAYER

# f = fireball.Fire()
# f.rect.topleft = (30, 30)

_HANDLER.add_entity(test.Test())
_HANDLER.add_entity(singleton.PLAYER)
_HANDLER.add_entity(m)
_HANDLER.add_entity(p)
_HANDLER.add_entity(p2)
# STATE.add_entity(f)
# STATE.add_entity(ph)


# grass
left = -2
right = 3
grass_count = 200


# left = 0
# right = 1
# grass_count = 300
for x in range(left, right):
    for y in range(left, right):
        GG = grass.GrassHandler("assets/sprites/grass.json")
        GG.position.xy = (x * EGLOB.CHUNK_PIX_WIDTH, y * EGLOB.CHUNK_PIX_HEIGHT)
        GG.move_to_position()
        GG.calculate_rel_hitbox()
        for i in range(grass_count):
            GG.add_grass(random.randint(0, EGLOB.CHUNK_PIX_WIDTH-GG.assets.get_dimensions(0)[0]//3), random.randint(0, EGLOB.CHUNK_PIX_HEIGHT - GG.assets.get_dimensions(0)[1]//3))
        # print(GG.chunk, GG.p_chunk)
        _WORLD.add_env_obj(GG)


# -------------------------------------------------- #
# testing zone

# text
from engine.graphics import text
from engine.graphics.teffects import TypeWriter

TM = text.TextManager(Filehandler.load_font("assets/font.ttf", 30), "Hello World\nHello World\pThis is a longer sentence becasue I need words",
                      text.TextManager.ALIGN_LEFT, buffer_is_text=False)

TM.add_effect(TypeWriter.TypeWriter(TM, 1/15))

# ambience
AMB = ambient.Ambience()
# _WORLD.add_env_obj(AMB)
_HANDLER.add_entity(AMB)

WH = wind.WindHandler()
AMB.add_system(WH)

WH.add_wind(wind.Wind(0, 50, 20))

# spawning enemies
TIMER = clock.Timer(wait_time=3.0)

# -------------------------------------------------- #

_HANDLER.handle_changes()
eid = list(_HANDLER.priority_entities)[0]
print(_HANDLER.get_entity(eid))

clock.start()
while Window.running:
    # change this eventually to another class that handles ui and system related things
    if user_input.is_key_pressed(pygame.K_LSHIFT) and user_input.is_key_clicked(pygame.K_d):
        EGLOB.DEBUG = not EGLOB.DEBUG
    # ----------------------------------- #
    # update current scene
    if scenehandler.SceneHandler.CURRENT:
        fb.fill(scenehandler.SceneHandler.CURRENT.data["bg_color"])
        # ----------------------------------- #
        # testing
        TIMER.update()
        if TIMER.changed:
            TIMER.changed = False
            if len(m.layer.handler.entities) < 100:
                o = peasant.Peasant()
                o.position.xy = m.position.xy + (
                maths.normalized_random() * m.DETECT_RADIUS, maths.normalized_random() * m.DETECT_RADIUS)
                m.layer.handler.add_entity(o)
        # ----------------------------------- #
        # update and render everything
        scenehandler.SceneHandler.CURRENT.update(fb)

        # TM.render_text(fb, (0, 0), True)

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

# CLIENT.close()
engine.end()
