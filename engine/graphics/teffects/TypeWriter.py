from ..text import TextEffect
from engine.misc import clock


# -------------------------------------------------- #
# typewriter effect

class TypeWriter(TextEffect):
    def __init__(self, textmanager, freq: float):
        super().__init__(textmanager)
        self.timer = clock.Timer(freq)
        self.index = 0

    def update(self):
        self.timer.update()
        if self.timer.changed:
            self.timer.changed = False
            if self.index < len(self.tm.text):
                self.tm.append_to_buffer(self.tm.text[self.index])
                self.index += 1

