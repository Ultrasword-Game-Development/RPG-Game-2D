import pygame


# static variables
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 0, 0
PREV_WIDTH, PREV_HEIGHT, PREV_FLAGS, PREV_DEPTH, PREV_VSYNC = 0, 0, 0, 0, 0

INITIALIZED = False
FRAMEBUFFER = None
FB_WIDTH, FB_HEIGHT = 0, 0

INSTANCE = None
WIDTH, HEIGHT = 0, 0
FLAGS = 0
DEPTH = 0
VSYNC = 0
SCALING = False

INSTANCE_CHANGED = True
GLOBAL_CLOCK = None

# framebuffer scale and stuff
XSCALE, YSCALE = 1, 1


# static file
def create_instance(t: int, w: int, h: int, f: int = 0, b: int = 32, v: int = 1, framebuffer=False):
    """Only one window instance is available at a time"""
    global INITIALIZED, WIDTH, HEIGHT, FLAGS, DEPTH, VSYNC, INSTANCE, ORIGINAL_HEIGHT, ORIGINAL_WIDTH, FRAMEBUFFER, FB_WIDTH, FB_HEIGHT
    if not INITIALIZED:
        ORIGINAL_WIDTH, ORIGINAL_HEIGHT = w, h
        pygame.init()
        INITIALIZED = True
        INSTANCE = pygame.display.set_mode((w, h), flags=f, depth=b, vsync=v)
        if framebuffer:
            change_framebuffer(w, h, f)
        pygame.display.set_caption(t)
    else:
        INSTANCE = pygame.display.set_mode((w, h), flags=f, depth=b, vsync=v)
        pygame.display.set_caption(t)
    WIDTH, HEIGHT, FLAGS, DEPTH, VSYNC = w, h, f, b, v
    return INSTANCE


def set_title(title) -> None:
    """Set window title"""
    pygame.display.set_caption(title)


def set_icon(icon) -> None:
    """Set window icon"""
    pygame.display.set_icon(icon)


def get_instance():
    """returns the instance"""
    return INSTANCE


def get_instance_for_draw():
    """Return the instance and set chagned to True"""
    global INSTANCE_CHANGED
    INSTANCE_CHANGED = True
    return INSTANCE


def set_scaling(scale: tuple) -> None:
    """set whether or not the window should scale framebuffer"""
    global SCALING
    SCALING = scale


def fill_instance(color: tuple) -> None:
    """Fill instance with solid color"""
    global INSTANCE_CHANGED
    INSTANCE_CHANGED = True
    INSTANCE.fill(color)


def change_framebuffer(w: int, h: int, f: int) -> None:
    """change a framebuffer"""
    global FRAMEBUFFER, FB_WIDTH, FB_HEIGHT
    FRAMEBUFFER = pygame.Surface((w, h), flags=f).convert()
    FB_WIDTH = w
    FB_HEIGHT = h


def get_framebuffer():
    """returns the framebuffer"""
    return FRAMEBUFFER


def get_framebuffer_for_draw():
    """Return framebuffer and set changed to True"""
    global INSTANCE_CHANGED
    INSTANCE_CHANGED = True
    return FRAMEBUFFER


def handle_resize(resize_event) -> None:
    """Handle window resize event"""
    global PREV_WIDTH, PREV_HEIGHT, WIDTH, HEIGHT
    PREV_WIDTH, PREV_HEIGHT = WIDTH, HEIGHT
    WIDTH, HEIGHT = resize_event.x, resize_event.y


def create_clock(FPS: int) -> None:
    """Creates a pygame clock object"""
    global GLOBAL_CLOCK
    GLOBAL_CLOCK = pygame.time.Clock()


def fill_buffer(color: tuple) -> None:
    """fill instance framebuffer"""
    global INSTANCE
    FRAMEBUFFER.fill(color)


def push_buffer(offset: tuple) -> None:
    """push the framebuffer onto the window"""
    global INSTANCE_CHANGED, SCALING, WIDTH, HEIGHT
    INSTANCE.blit(FRAMEBUFFER if not SCALING else pygame.transform.scale(FRAMEBUFFER, (WIDTH, HEIGHT)), offset)
    INSTANCE_CHANGED = False


def draw_buffer(surface, pos: tuple) -> None:
    """draw onto framebuffer"""
    global INSTANCE_CHANGED
    FRAMEBUFFER.blit(surface, pos)
    INSTANCE_CHANGED = True


def draw(surface, pos: tuple) -> None:
    """draw directly onto instance"""
    global INSTANCE_CHANGED
    INSTANCE_CHANGED = True
    INSTANCE.blit(surface, pos)


def mouse_window_to_framebuffer(mouse_pos: tuple) -> tuple:
    """Return the framebuffer coords of the mouse"""
    # is buggy
    return (mouse_pos[0] / WIDTH * FB_WIDTH, mouse_pos[1] / HEIGHT * FB_HEIGHT)
