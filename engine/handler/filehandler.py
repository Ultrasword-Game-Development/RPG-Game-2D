import pygame
import pickle

from ..world import chunk
from .. import singleton

"""
Filehandler stores + handles files
- images
- audio files
"""


class Filehandler:
    # str : surface
    LOADED_IMAGES = {}
    # str: {int: font}
    LOADED_FONTS = {}

    # -------------------------------------------------- #
    # file loading

    @classmethod
    def get_image(cls, path: str):
        """Loads images + converts to alpha so they are faster to use"""
        if path in cls.LOADED_IMAGES:
            return cls.LOADED_IMAGES[path]
        cls.LOADED_IMAGES[path] = pygame.image.load(path).convert_alpha()
        return cls.LOADED_IMAGES[path]

    @classmethod
    def get_image_and_scale_float(cls, path: str, scale: list):
        """
        Loads images + optional scaling + converts to alpha so they are faster to use
        - scale = list [float, float]
        multiplies the original width by float values
        """
        if path in cls.LOADED_IMAGES:
            i_size = cls.LOADED_IMAGES[path].get_size()
            return pygame.transform.scale(cls.LOADED_IMAGES[path],
                                          (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))
        cls.LOADED_IMAGES[path] = pygame.image.load(path).convert_alpha()
        i_size = cls.LOADED_IMAGES[path].get_size()
        return pygame.transform.scale(cls.LOADED_IMAGES[path],
                                      (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))

    # -------------------------------------------------- #
    # font / text loading
    @classmethod
    def load_font(cls, path: str, size: int):
        """Load .ttf files / fonts for the program + cache"""
        # if font is already loaded with the size
        if path in cls.LOADED_IMAGES and size in cls.LOADED_FONTS[path]:
            return cls.LOADED_FONTS[path][size]
        # load the font
        font = pygame.font.Font(path, size)
        # cache font
        if path not in cls.LOADED_FONTS:
            cls.LOADED_FONTS[path] = {}
        cls.LOADED_FONTS[path][size] = font
        return font

# -------------------------------------------------- #
# chunk saving


class ChunkSaver:
    @classmethod
    def save_chunk(cls, chunk, filepath):
        """Given a chunk and a file, we can save a chunk"""
        with open(filepath, 'wb') as file:
            data = {"pos": chunk.world_chunk_tile,
                    "tilemap": [[chunk.tilemap[y][x].to_dict() for x in range(singleton.TILEMAP_WIDTH)] for y in
                                range(singleton.TILEMAP_HEIGHT)]}
            pickle.dump(data, file)
            file.close()

    @classmethod
    def load_chunk(cls, filepath):
        """load a chunk given a file"""
        with open(filepath, 'rb') as file:
            data = pickle.load(file)
            file.close()
        r = chunk.Chunk(data["pos"][0], data["pos"][1])
        print("Finish implementing file saving stuff")
        return r
