
import pygame

import soragl as SORA
from soragl import scene
from soragl import physics

from soragl import base_objects

# -------------------------------------------------------------- #

class UI(scene.World):

    """
    UI is world
    - world handles entities

    each ui object = entity
    - entity contains sprite data + signals:
        - key events
        - mouse click events
        - mouse enter / exit events
    """

    def __init__(self, scene, options: dict, render_distance: int = 1, aspects: dict = {}, chunks: dict = {}):
        options["tilepixw"] = 1000
        options["tilepixh"] = 1000
        super().__init__(scene, options, render_distance, aspects, chunks)


# -------------------------------- #

class UIObject(physics.Entity):
    def __init__(self, name: str = None):
        """An object in the UI""" 
        super().__init__(name)
        self.c_sprite = base_objects.Sprite(1, 1, None, None, flags=pygame.SRCALPHA)
    
    def on_ready(self):
        """When UI Object is ready"""
        self.add_component(self.c_sprite)
        self.add_component(base_objects.SpriteRenderer())




# -------------------------------- #
# aspects

class UIRendererAspect(base_objects.SpriteRendererAspect):
    def __init__(self):
        super().__init__()
    
    def handle_entity(self, entity):
        """Render a UI Object"""
        c_sprite = entity.c_sprite
        # they will always have a sprite
        # render the sprite
        if c_sprite.scale_size:
            SORA.FRAMEBUFFER.blit(
                pgtrans.scale(c_sprite._sprite, c_sprite.scale_size),
                entity.position - (c_sprite.hwidth, c_sprite.hheight),
            )
            return
        SORA.FRAMEBUFFER.blit(
            c_sprite._sprite, entity.position - (c_sprite.hwidth, c_sprite.hheight)
        )

