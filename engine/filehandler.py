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
        if path in Filehandler.LOADED_FILES:
            return Filehandler.LOADED_FILES[path]
        Filehandler.LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        return Filehandler.LOADED_FILES[path]

    @staticmethod
    def get_image_and_scale(path: str, scale: list):
        """Loads images + optional scaling + converts to alpha so they are faster to use"""
        if path in Filehandler.LOADED_FILES:
            i_size = Filehandler.LOADED_FILES[path].get_size()
            return pygame.transform.scale(Filehandler.LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))
        Filehandler.LOADED_FILES[path] = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(Filehandler.LOADED_FILES[path], (int(i_size[0] * scale[0]), int(i_size[1] * scale[1])))


