

import soragl as SORA

from soragl.ui import ui

# -------------------------------- #

from scripts.environment import grass
from scripts.attacks import fireball

_g_asset = grass.GrassAssets("assets/sprites/grass.json")


# -------------------------------- #


class Hotbar(ui.UIObject):
    def __init__(self):
        super().__init__("Hotbar")
        # draw on the sprite
        print(_g_asset._rsequence)
        self.c_sprite.area = (16 * len(_g_asset._rsequence), 16)

        # render out frames from grasshandler assets
        for x, frame in enumerate(_g_asset._rsequence):
            self.c_sprite.sprite.blit(frame.frame, (x * 16, 0))
    
    def on_ready(self):
        super().on_ready()
        # add other components

    def update(self):
        """Update the hotbar"""
        pass


class UIIcon(ui.UIObject):
    def __init__(self, name: str = "UIObject"):
        super().__init__(name)
        self.c_sprite.area = (16 * 3, 16 * 8)
        for y in range(8):
            for x in range(3):
                self.c_sprite.sprite.blit(fireball.F_ANIM_CACHE.get_frame(x, 45 * y), (x * 16, y * 16))
    




