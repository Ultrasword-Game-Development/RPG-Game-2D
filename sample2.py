import pygame
import soragl as SORA
import struct

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects, mgl

# ------------------------------ #
# setup
SORA.initialize(
    {
        "fps": 30,
        "window_size": [1280, 720],
        "window_flags": pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF,
        "window_bits": 32,
        "framebuffer_flags": pygame.SRCALPHA,
        "framebuffer_size": [1280 // 3, 720 // 3],
        "framebuffer_bits": 32,
        "debug": True,
    }
)

SORA.create_context()

# ------------------------------ #
# import gl?
if SORA.is_flag_active(pygame.OPENGL):
    from soragl import mgl
    from soragl.mgl import ModernGL
    print("Configured Pygame for OpenGL")


# ------------------------------ #
# post setup

mgl.ModernGL.create_context(
    options={
        "standalone": False,
        "gc_mode": "context_gc",
        "clear_color": [0.0, 0.0, 0.0, 1.0],
    }
)

shader = mgl.ShaderProgram("assets/shaders/default.glsl")
# shader = mgl.ShaderProgram("assets/shaders/default3d.glsl")

vertices = mgl.Buffer(
    "36f",
    [
        -1.0,
        -1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        1.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
)
indices = mgl.Buffer("6i", [0, 1, 2, 3, 0, 2])
vattrib = mgl.VAO("assets/shaders/default.glsl")
vattrib.add_attribute("3f", "vvert")
vattrib.add_attribute("2f", "vuv")
vattrib.add_attribute("4f", "vcolor")
# add attribs?
vattrib.create_structure(vertices, indices)

# ------------------------------ #
# scripts imports

# ------------------------------ #
# scripts setup


animation.Category.load_category("assets/sprites/tomato.json")
registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")[
    "idle"
].get_registry()


image = SORA.load_image("assets/sprites/tomato.png")
potato = SORA.load_image("assets/sprites/potato-2.png")
__ss = animation.SpriteSheet(image, 16, 16, 0, 0)

sc = scene.Scene(config=scene.load_config(scene.Scene.DEFAULT_CONFIG))
scw = sc.make_layer(sc.get_config(), 1)
scw.get_chunk(0, 0)

sce = physics.Entity()
sceparticle = physics.ParticleHandler(create_func="custom", update_func="custom")
sceparticle.position += (200, 150)
sceparticle["interval"] = 0.5

# add entities to world first
scw.add_entity(sce)
scw.add_entity(sceparticle)

# entity comp
sce.add_component(base_objects.Sprite(0, 0, potato))
sce.add_component(base_objects.SpriteRenderer())
sce.add_component(base_objects.Collision2DComponent())
sce.position += (100, 100)
sce.area = (20, 20)
# sce1.static = True

# physics
sce.add_component(base_objects.Collision2DComponent())

# aspects
scw.add_aspect(base_objects.TileMapDebug())
scw.add_aspect(base_objects.SpriteRendererAspect())
scw.add_aspect(base_objects.Collision2DRendererAspectDebug())
scw.add_aspect(base_objects.RenderableAspect())

# push scene
scene.SceneHandler.push_scene(sc)

# ------------------------------ #
# post testing

tm = scw.get_aspect(base_objects.TileMapDebug)
tm.set_sprite_data("assets/sprites/shovel.png", pygame.Rect(0, 0, 16, 16))
tm.add_tile_global("assets/sprites/shovel.png", 0, 0)


# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    # SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    SORA.FRAMEBUFFER.fill((0, 0, 0, 255))
    SORA.DEBUGBUFFER.fill((0, 0, 0, 0))
    # pygame update + render
    registry.update()
    scene.SceneHandler.update()

    if SORA.is_key_clicked(pygame.K_d) and SORA.is_key_pressed(pygame.K_LSHIFT):
        SORA.DEBUG = not SORA.DEBUG

    # SORA.FRAMEBUFFER.blit(SORA.DEBUGBUFFER, (0, 0))

    # moderngl render
    ModernGL.update_context()
    ModernGL.CTX.clear(
        ModernGL.CLEARCOLOR[0],
        ModernGL.CLEARCOLOR[1],
        ModernGL.CLEARCOLOR[2],
        ModernGL.CLEARCOLOR[3],
    )
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    vattrib.change_uniform_scalar("utime", SORA.ENGINE_UPTIME % 10000)
    vattrib.change_uniform_scalar(
        "framebuffer", mgl.Texture.pg2gltex(SORA.FRAMEBUFFER, "fb")
    )
    vattrib.change_uniform_scalar(
        "debugbuffer", mgl.Texture.pg2gltex(SORA.DEBUGBUFFER, "db")
    )

    # vao.render(mode=mgl.moderngl.TRIANGLES)
    vattrib.render()
    ModernGL.CTX.disable(mgl.moderngl.BLEND)

    # push frame
    # SORA.push_framebuffer()
    pygame.display.flip()
    # update events
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock tick
    SORA.CLOCK.tick(SORA.FPS)
    SORA.update_time()

pygame.quit()
