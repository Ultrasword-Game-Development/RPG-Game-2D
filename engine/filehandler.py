import pygame
import json

from dataclasses import dataclass

# pygame flags
SRC_ALPHA = pygame.SRCALPHA

# TODO - design a resizing system when loading images


# load json
def get_json_data(path: str):
    """Get the JSON data"""
    with open(path, 'r') as file:
        data = json.load(file)
        file.close()
    return data


"""
Images

- for image files:
    - png
    - jpg

Caches all the loaded image files unless using get_image_without_cache()
"""

IMAGES = {}

def get_image(img):
    """get and image"""
    if not IMAGES.get(img):
        if img.endswith(".png"):
            image = pygame.image.load(img).convert_alpha()
        else:
            image = pygame.image.load(img).convert()
        IMAGES[img] = image
    return IMAGES[img]


def get_image_without_cache(img):
    """get image wihtout cache or convert"""
    if img.endswith(".png"):
        return pygame.image.load(img).convert_alpha()
    return pygame.image.load(img).convert()


def scale(img, size):
    """scale images"""
    return pygame.transform.scale(img, size)


def xflip(img):
    """flips image across y axis"""
    return pygame.transform.flip(img, True, False)


def yflip(img):
    """flips image across x axis"""
    return pygame.transform.flip(img, False, True)


def make_surface(width, height, flags=0):
    """Make a surface object and return it"""
    return pygame.Surface((width, height), flags).convert_alpha()


def crop_image(source, target, source_area):
    """Crop source onto target given areas"""
    target.blit(source, (0, 0), source_area)


"""
Fonts

- loads fonts and stores them
    - .ttf

Fonts are cached and can be retrieved via get_font(string path)

< ------ important -------- >
When loading fonts, make sure to load from relative position from program

- system fonts will not be loaded
"""

FONTS = {}

class FontObject:
    """
    Font object
    
    - holds font path
    - dict of all sizes of the font
    """
    def __init__(self, path: str):
        """FontObject constructor"""
        self.size = {}
        self.path = path

    def get_font_size(self, font_size: int):
        """Get a font size"""
        if not self.size.get(font_size):
            self.size[font_size] = pygame.font.Font(self.path, font_size)
        return self.size[font_size]


def get_font(path: str):
    """Get a font"""
    if not FONTS.get(path):
        FONTS[path] = FontObject(path)
    return FONTS[path]


"""
Audio/Music

- loads music files:
    - mp3
    - wav
    - ogg

pygame.mixer objects are cached
"""

# audio documentation
#   https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
#   https://www.pygame.org/docs/ref/music.html
AUDIO = {}

# channel documentation:
#   https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel
CHANNELS = {}

def get_audio(path: str):
    """Get and cache audio"""
    if not AUDIO.get(path):
        AUDIO[path] = pygame.mixer.Sound(path)
    return AUDIO[path]


def create_channel(channel: int):
    """Create an audio channel"""
    if not CHANNELS.get(channel):
        CHANNELS[channel] = pygame.mixer.Channel(channel)
    return CHANNELS[channel]


class AudioRegistry:
    """
    Registry for a singular audio source
    """
    
    def __init__(self, audio_path: str):
        """Audio Registry constructor"""
        self.audio_path = audio_path
        # load audio
        self.audio_data = get_audio(audio_path)
    
    def play_audio(self, volume: int = 1, channel: int = 0, loops: int = 0, maxtime: int = 0, fadetime: int = 0):
        """Play the audio given volume and channel"""
        CHANNELS[channel].set_volume(volume / 100)
        CHANNELS[channel].play(self.audio_data, loops, maxtime, fadetime)
    
    def serialize(self):
        """Serialize method for AudioRegistry"""
        pass

