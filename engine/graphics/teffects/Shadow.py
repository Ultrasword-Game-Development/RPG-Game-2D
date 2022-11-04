from ..text import TextEffect


# -------------------------------------------------- #
# shadw effect

class Shadow(TextEffect):
    def __init__(self, textmanager, freq: float):
        super().__init__(textmanager)

    def post_update(self):
        pass


