from dataclasses import dataclass

@dataclass(init=False)
class Tile:
    """
    Tile Dataclass Object
    - holds simple data
    """
    position: tuple

    def __init__(self, x, y):
        """
        Constructor for Tile
        contains:
        - position      = (int, int)
        - world_hitbox  = pygame.Rect
        - data          = dict {str: hashable /pickle-able value}
        """
        self.position = (x, y)

class BigTile:
    def __init__(self, x, y):
        self.position = (x, y)

import time

T = 8 * 8 * 10 * 10000
st = time.time()

for i in range(T):
    Tile(1,2)
print(time.time()-st)
st = time.time()
for i in range(T):
    BigTile(1, 2)
print(time.time()-st)

