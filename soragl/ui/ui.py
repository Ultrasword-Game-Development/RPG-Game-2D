

import soragl as SORA
from soragl import scene
from soragl import physics

from soragl import base_objects

# -------------------------------------------------------------- #

class UI:

    """
    UI is world
    - world handles entities

    each ui object = entity
    - entity contains sprite data + signals:
        - key events
        - mouse click events
        - mouse enter / exit events
    """

    def __init__(self, world: "World"):
        self._world = world
    
    
# -------------------------------- #

class UIObject(physics.Entity):
    def __init__(self, name: str = None):
        super().__init__(name)
        """An object in the UI"""
        self._signals = {}

