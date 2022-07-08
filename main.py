import pygame
from engine.filehandler import *


WINDOW_CAPTION = "RPG Game"
WINDOW_SIZE = [1280, 720]

FPS = 30

window = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
pygame.display.set_caption(WINDOW_CAPTION)

clock = pygame.time.Clock()


image = Filehandler.get_image("assets/")





running = True

while running:
    window.fill((255, 255, 255))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()

