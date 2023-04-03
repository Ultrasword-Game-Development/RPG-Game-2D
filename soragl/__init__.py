print("Thanks for using Sora Engine! v0.1")

import pygame
import time
import sys


_VERSION = "0.1.0"

DEBUG = True

# ------------------------------------------------ #
# system / environment data
# ------------------------------------------------ #

OS_WINDOWS = "win"
OS_MACOS = "darwin"
OS_LINUX = "linux"


def get_os():
    """Checks the operating system."""
    if sys.platform.startswith(OS_WINDOWS):
        return OS_WINDOWS
    elif sys.platform.startswith(OS_MACOS):
        return OS_MACOS
    elif sys.platform.startswith(OS_LINUX):
        return OS_LINUX
    else:
        return "unknown"


# ------------------------------------------------ #
# time + time + time
# ------------------------------------------------ #

ENGINE_UPTIME = 0
ENGINE_START_TIME = 0

START_TIME = 0
END_TIME = 0
DELTA = 0


def start_engine_time():
    """Starts engine time."""
    global ENGINE_START_TIME, START_TIME, END_TIME, DELTA
    ENGINE_START_TIME = time.time()
    START_TIME = ENGINE_START_TIME
    update_time()


def update_time():
    """Updates time."""
    global START_TIME, END_TIME, DELTA, ENGINE_UPTIME
    END_TIME = time.time()
    DELTA = END_TIME - START_TIME
    START_TIME = END_TIME
    ENGINE_UPTIME += DELTA
    # update all clocks
    update_global_clocks()


def pause_time(t: float):
    """Pauses time for a certain amount of time."""
    time.sleep(t)


def get_current_time():
    """Returns the current system time"""
    return START_TIME


# ------------------------------------------------ #
# global clock queue
# ------------------------------------------------ #

ALL_CLOCKS = {}
ACTIVE_CLOCKS = set()
REMOVE_ARR = set()


def deactivate_timer(timer):
    """Deactivate a timer"""
    REMOVE_ARR.add(timer.hash)


def activate_timer(timer):
    """Activate a timer"""
    ACTIVE_CLOCKS.add(timer.hash)


def get_timer(limit: float = 0, loop: bool = False):
    """Get a timer object"""
    c = Timer(limit, loop)
    ALL_CLOCKS[c.hash] = c
    activate_timer(c)
    return c


def update_global_clocks():
    """Update all active clocks"""
    for c in ACTIVE_CLOCKS:
        ALL_CLOCKS[c].update()
    for c in REMOVE_ARR:
        ACTIVE_CLOCKS.remove(c)
    REMOVE_ARR.clear()


# ------------------------------------------------ #
# timer class
# ------------------------------------------------ #


class Timer:
    def __init__(self, limit: float, loop: bool):
        self.hash = hash(self)
        self.initial = get_current_time()
        self.passed = 0
        self.loopcount = 0
        self.limit = limit
        self.loop = loop

    def update(self):
        """Updates the clock - throws a signal when finished"""
        self.passed += DELTA
        # to implement sending signals -- when completed!
        # print(self.passed)
        if self.passed > self.limit:
            # -- emit a signal
            self.passed = 0
            self.loopcount += 1
            if not self.loop:
                deactivate_timer(self)

    def reset_timer(self, time: float = 0):
        """Reset the timer"""
        self.initial = get_current_time()
        self.passed = 0
        self.loopcount = 0


# ------------------------------------------------ #
# window variables
# ------------------------------------------------ #

FPS = 60
WSIZE = [1280, 720]
WPREVSIZE = [1280, 720]
WFLAGS = pygame.RESIZABLE | pygame.DOUBLEBUF
WBITS = 32
FFLAGS = pygame.SRCALPHA
FPREVSIZE = [1280, 720]
FSIZE = [1280, 720]
FHSIZE = [FSIZE[0] // 2, FSIZE[1] // 2]
FBITS = 32

MODERNGL = False


# setup engine
def initialize(options: dict = {}) -> None:
    """Initialize Sora Engine with options"""
    global FPS, WSIZE, WFLAGS, WBITS, FFLAGS, FSIZE, FHSIZE, FBITS, MODERNGL, DEBUG
    FPS = options["fps"] if "fps" in options else 60
    WSIZE = options["window_size"] if "window_size" in options else [1280, 720]
    WFLAGS = (
        options["window_flags"]
        if "window_flags" in options
        else pygame.RESIZABLE | pygame.DOUBLEBUF
    )
    WBITS = options["window_bits"] if "window_bits" in options else 32
    FFLAGS = (
        options["framebuffer_flags"]
        if "framebuffer_flags" in options
        else pygame.SRCALPHA
    )
    FSIZE = options["framebuffer_size"] if "framebuffer_size" in options else WSIZE
    FHSIZE = [FSIZE[0] // 2, FSIZE[1] // 2]
    FBITS = options["framebuffer_bits"] if "framebuffer_bits" in options else 32
    DEBUG = options["debug"] if "debug" in options else False
    # add options as required!
    MODERNGL = is_flag_active(pygame.OPENGL)
    if MODERNGL:
        from . import mgl


# check if certain flags are active
def is_flag_active(flag: int):
    """Checks if a flag is active."""
    return bool(WFLAGS & flag)


# ------------------------------------------------ #
# window/camera data
# ------------------------------------------------ #
WINDOW = None
FRAMEBUFFER = None
DEBUGBUFFER = None
CLOCK = None
RUNNING = False

OFFSET = [0, 0]
iOFFSET = [0, 0]


def set_offset(x: float, y: float):
    """Set the engine offset"""
    global OFFSET, iOFFSET
    OFFSET[0] = x
    OFFSET[1] = y
    iOFFSET[0] = round(x)
    iOFFSET[1] = round(y)


def create_context():
    """Creates window context and Framebuffer for Sora Engine."""
    global WINDOW, FRAMEBUFFER, DEBUGBUFFER, CLOCK, RUNNING
    WINDOW = pygame.display.set_mode(WSIZE, WFLAGS, WBITS)
    FRAMEBUFFER = pygame.Surface(FSIZE, FFLAGS, FBITS)
    DEBUGBUFFER = pygame.Surface(FSIZE, FFLAGS | pygame.SRCALPHA, FBITS)
    CLOCK = pygame.time.Clock()
    RUNNING = True


def push_framebuffer():
    """Pushes framebuffer to window."""
    if MODERNGL:
        # push frame buffer to moderngl window context
        mgl.ModernGL.pre_render()
        mgl.ModernGL.render_frame()
        pygame.display.flip()
    else:
        # render frame buffer texture to window!
        WINDOW.blit(pygame.transform.scale(FRAMEBUFFER, WSIZE), (0, 0))
        WINDOW.blit(pygame.transform.scale(DEBUGBUFFER, WSIZE), (0, 0))
        pygame.display.update()


def refresh_buffers(color):
    """Refreshes framebuffer and debugbuffer"""
    FRAMEBUFFER.fill(color)
    DEBUGBUFFER.fill((0, 0, 0, 0))


def update_window_resize(event):
    """Updates window size and framebuffer size."""
    global WSIZE, WPREVSIZE, FSIZE, FPREVSIZE
    WPREVSIZE[0], WPREVSIZE[1] = WSIZE[0], WSIZE[1]
    WSIZE[0], WSIZE[1] = event.x, event.y


# TODO - changing fb res

# ------------------------------------------------ #
# hardware data -- input [mouse]
# ------------------------------------------------ #

MOUSE_POS = [0, 0]
MOUSE_MOVE = [0, 0]
MOUSE_BUTTONS = [False, False, False]
MOUSE_PRESSED = set()
MOUSE_SCROLL = [0, 0]
MOUSE_SCROLL_POS = [0, 0]


def update_mouse_pos(event):
    """Update mouse position."""
    MOUSE_MOVE[0], MOUSE_MOVE[1] = event.rel
    MOUSE_POS[0], MOUSE_POS[1] = event.pos


def update_mouse_press(event):
    """Update mouse button press."""
    if 3 < event.button > 1:
        return
    MOUSE_BUTTONS[event.button - 1] = True
    MOUSE_PRESSED.add(event.button - 1)


def update_mouse_release(event):
    """Update mouse button release."""
    # in case of scrolling
    if 3 < event.button > 1:
        return
    MOUSE_BUTTONS[event.button - 1] = False


def update_mouse_scroll(event):
    """Update mouse scroll."""
    MOUSE_SCROLL_POS[0] += event.precise_x
    MOUSE_SCROLL_POS[1] += event.precise_y
    MOUSE_SCROLL[0], MOUSE_SCROLL[1] = event.precise_x, event.precise_y


# ------------------------------------------------ #
# hardware data -- input [keyboard]
# ------------------------------------------------ #

KEYBOARD_KEYS = {}
KEYBOARD_PRESSED = set()

# ensure that the error does not occur
for i in range(0, 3000):
    KEYBOARD_KEYS[i] = False


def update_keyboard_down(event):
    """Update keyboard key press."""
    KEYBOARD_KEYS[event.key] = True
    KEYBOARD_PRESSED.add(event.key)


def update_keyboard_up(event):
    """Update keyboard key release."""
    KEYBOARD_KEYS[event.key] = False


# ------------------------------------------------ #
# hardware data -- input [key + mouse]
# ------------------------------------------------ #


def update_hardware():
    """Updates the mouse"""
    global MOUSE_SCROLL
    # print("DEBUG:", MOUSE_PRESSED, KEYBOARD_PRESSED)
    MOUSE_PRESSED.clear()
    MOUSE_SCROLL = [0, 0]
    KEYBOARD_PRESSED.clear()


def get_mouse_rel():
    """Returns mouse position."""
    return (
        MOUSE_POS[0] / WSIZE[0] * FSIZE[0],
        MOUSE_POS[1] / WSIZE[1] * FSIZE[1],
    )


def get_mouse_abs():
    """Returns mouse position."""
    return (MOUSE_POS[0], MOUSE_POS[1])


def is_mouse_pressed(button):
    """Returns if mouse button is pressed."""
    return MOUSE_BUTTONS[button]


def is_mouse_clicked(button):
    """Returns if mouse button is clicked."""
    return button in MOUSE_PRESSED


def is_key_pressed(key):
    """Returns if key is pressed."""
    if not key in KEYBOARD_KEYS:
        KEYBOARD_KEYS[key] = False
    return KEYBOARD_KEYS[key]


def is_key_clicked(key):
    """Returns if key is clicked."""
    return key in KEYBOARD_PRESSED


def handle_pygame_events():
    """Handles pygame events."""
    global RUNNING
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
        elif e.type == pygame.KEYDOWN:
            # keyboard press
            update_keyboard_down(e)
        elif e.type == pygame.KEYUP:
            # keyboard release
            update_keyboard_up(e)
        elif e.type == pygame.MOUSEMOTION:
            # mouse movement
            update_mouse_pos(e)
        elif e.type == pygame.MOUSEWHEEL:
            # mouse scroll
            update_mouse_scroll(e)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            # mouse press
            update_mouse_press(e)
        elif e.type == pygame.MOUSEBUTTONUP:
            # mouse release
            update_mouse_release(e)
        elif e.type == pygame.WINDOWRESIZED:
            # window resized
            update_window_resize(e)


# ------------------------------------------------ #
# filehandler
# ------------------------------------------------ #
IMAGES = {}
CHANNELS = {}
AUDIO = {}
FONTS = {}


# textures
def load_image(path):
    """Loads image from file."""
    if path in IMAGES:
        return IMAGES[path]
    IMAGES[path] = pygame.image.load(path).convert_alpha()
    return IMAGES[path]


def scale_image(image, size):
    """Scales image to size."""
    return pygame.transform.scale(image, size)


def load_and_scale(image, size):
    """Loads and scales image to size."""
    return scale_image(load_image(image), size)


def make_surface(width, height, flags=0, depth=32):
    """Creates a new surface."""
    return pygame.Surface((width, height), flags, depth).convert_alpha()


# audio
def make_channel(name):
    """Creates a new channel."""
    CHANNELS[name] = pygame.mixer.Channel(len(CHANNELS))


def load_audio(path):
    """Loads audio from file."""
    if path in AUDIO:
        return AUDIO[path]
    AUDIO[path] = pygame.mixer.Sound(path)
    return AUDIO[path]


def play_audio(path, channel):
    """Plays audio on channel."""
    CHANNELS[channel].play(load_audio(path))


def play_music(path):
    """Plays music."""
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)


def stop_music():
    """Stops music."""
    pygame.mixer.music.stop()


def set_volume(volume):
    """Sets volume."""
    pygame.mixer.music.set_volume(volume)


# text / fonts
def load_font(path, size):
    """Loads font from file."""
    fs = f"{path}|{size}"
    if fs in FONTS:
        return FONTS[fs]
    FONTS[fs] = pygame.font.Font(path, size)
    return FONTS[fs]
