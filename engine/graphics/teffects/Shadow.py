from ..text import TextEffect


# -------------------------------------------------- #
# typewriter effect

class TypeWriter(TextEffect):
    def __init__(self, textmanager, freq: float):
        super().__init__(textmanager)

    def post_update(self):
        pass


