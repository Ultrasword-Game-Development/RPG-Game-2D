import pygame

from . import singleton as EGLOB


class Window:
    instance = None
    running = False

    PREV_WIDTH = 0
    PREV_HEIGHT = 0

    WIDTH = 0
    HEIGHT = 0
    FLAGS = 0 
    BITS = 0
    TITLE = ""

    @classmethod
    def create_window(cls, title: str, width: int, height: int, flags: int, bits: int):
        """Create a window with the given information"""
        cls.instance = pygame.display.set_mode((width, height), flags, bits)
        pygame.display.set_caption(title)
        cls.running = True
        cls.TITLE = title
        cls.WIDTH = width
        cls.HEIGHT = height
        cls.FLAGS = flags
        cls.BITS =  bits

        EGLOB.WINDOW_WIDTH = width
        EGLOB.WINDOW_HEIGHT = height

    @classmethod
    def set_icon(cls, surface):
        """Set the icon surface"""
        pygame.display.set_icon(surface)
    
    @classmethod
    def handle_resize(cls, resize_event):
        cls.PREV_WIDTH, cls.PREV_HEIGHT = cls.WIDTH, cls.HEIGHT
        cls.WIDTH, cls.HEIGHT = resize_event.x, resize_event.y
        # also scale input in input
    
    @classmethod
    def create_framebuffer(cls, width, height, flags=0, bits=32):
        """Create a framebuffer object"""
        EGLOB.FB_WIDTH = width
        EGLOB.FB_HEIGHT = height
        EGLOB.FBWHALF = width//2
        EGLOB.FBHHALF = height//2
        return pygame.Surface((width, height), flags=flags, depth=bits).convert_alpha()




