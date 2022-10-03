import pygame
pygame.init()

from .handler import *
from .misc import *
from .network import *
from .graphics import *
from .gamesystem import *
from .world import *

from . import singleton
from . import window

# from .gl import *


print("Initialized Engine")


def end():
    pygame.quit()
