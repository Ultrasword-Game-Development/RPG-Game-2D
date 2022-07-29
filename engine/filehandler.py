import pygame
import pickle

from . import globals
from . import chunk

"""
Filehandler stores + handles files
- images
- audio files
"""

class Filehandler:
    LOADED_FILES = {}

    @staticmethod
    def get_image(path: str):
        """Loads images + converts to alpha so they are faster to use"""
        if path in Filehandler.LOADED_FILES:
            return Filehandler.LOADED_FILES[path]
        Filehandler.LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        return Filehandler.LOADED_FILES[path]

    @staticmethod
    def get_image_and_scale_float(path: str, scale: list):
        """
        Loads images + optional scaling + converts to alpha so they are faster to use
        - scale = list [float, float]
        multiplies the original width by float values
        """
        if path in Filehandler.LOADED_FILES:
            i_size = Filehandler.LOADED_FILES[path].get_size()
            return pygame.transform.scale(Filehandler.LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))
        Filehandler.LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        i_size = Filehandler.LOADED_FILES[path].get_size()
        return pygame.transform.scale(Filehandler.LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))


class ChunkSaver:
    @classmethod
    def save_chunk(cls, chunk, filepath):
        """Given a chunk and a file, we can save a chunk"""
        with open(filepath, 'wb') as file:
            data = {"pos": chunk.world_chunk_tile, "tilemap": [[chunk.tilemap[y][x].to_dict() for x in range(globals.TILEMAP_WIDTH)] for y in range(globals.TILEMAP_HEIGHT)]}
            ds = pickle.dump(data, file)
            file.close()
    
    @classmethod
    def load_chunk(cls, filepath):
        """load a chunk given a file"""
        with open(filepath, 'rb') as file:
            data = pickle.load(file)
            file.close()
        r = chunk.Chunk(data["pos"][0], data["pos"][1])
        for x in range(globals.TILEMAP_WIDTH):
            for y in range(globals.TILEMAP_HEIGHT):
                r.get_tile_at(x, y).position = data["tilemap"][y][x]["pos"]
                r.get_tile_at(x, y).set_sprite(data["tilemap"][y][x]["path"])
        return r
    
    
