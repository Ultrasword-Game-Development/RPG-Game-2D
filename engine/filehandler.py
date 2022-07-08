import pygame


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
        if path in LOADED_FILES:
            return LOADED_FILES[path]
        LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        return LOADED_FILES[path]

    @staticmethod
    def get_image_and_scale(path: str, scale: list):
        """Loads images + optional scaling + converts to alpha so they are faster to use"""
        if path in LOADED_FILES:
            i_size = LOADED_FILES[path].get_size()
            return pygame.transform.scale(LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))
        LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))


