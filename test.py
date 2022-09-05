import pygame

from engine import gl
import OpenGL
from OpenGL import GL


pygame.init()


window = pygame.display.set_mode([500, 500], pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

# -------- GL Setup ---------- #

GL.glViewport(0, 0, 500, 500)
GL.glClearColor(0.4, 0.4, 0.4, 1.0)

# ------ Test SHADER --- ----- #

vs, fs = compile_shader(GL.GL_VERTEX_SHADER, vert_shader), compile_shader(GL.GL_FRAGMENT_SHADER)

# ---------------------------- #

running = True
while running:
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    pygame.display.flip()
    clock.tick(30)


pygame.quit()



