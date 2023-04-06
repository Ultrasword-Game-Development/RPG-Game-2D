"""
Misc functions:
- io
- idk
"""

import pygame

import soragl as SORA
from soragl import scene, signal

# ------------------------------------------------------------ #
# misc functions!
"""
General Misc Functions
"""
# ------------------------------------------------------------ #

def fread(path):
    """Read a file and return its content as a string"""
    with open(path, 'r') as f:
        return f.read()

def fwrite(path, data: str):
    """Write a string to a file"""
    with open(path, 'w') as f:
        f.write(data)


def recursive_retrieve_parent_classes(obj, level=0):
    """Recursively retrieve all parent classes of an object"""
    result = []
    itt = obj.__class__.__bases__ if level == 0 else obj.__bases__
    if itt:
        for base in itt:
            if base == object:
                continue
            result.append(base)
            result += recursive_retrieve_parent_classes(base, level + 1)
    return result


# ------------------------------------------------------------ #
# misc classes
"""
Misc Classes
- good base classes for random functional components
"""
# ------------------------------------------------------------ #

class Dictionary:
    def __init__(self):
        self._dict = {}
    
    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

# ------------------------------------------------------------ #
# misc user input options
"""
User Input Options
- Mouse locking (lock mouse to center of screen)
- Mouse sensitivity (how fast the mouse moves)
- Keybinds (change keybinds)
"""
# ------------------------------------------------------------ #

class MouseLocking(scene.Aspect):
    def __init__(self, lockx:float, locky: float, locked: bool = True, hide_mouse: bool = True):
        super().__init__(None)
        self._priority = 100
        # private
        self._lock_position = (lockx, locky)
        self._hide_mouse = False
        self.hidden = hide_mouse

        # public
        self.locked = locked
        self.delta = [0, 0]
    
    @property
    def hidden(self):
        """Is the mouse hidden?"""
        return self._hide_mouse
    
    @hidden.setter
    def hidden(self, value: bool):
        """Set the mouse hidden"""
        self._hide_mouse = value
        pygame.mouse.set_visible(not self._hide_mouse)

    def update(self):
        """Update the mouse locking"""
        if self.locked:
            mpos = SORA.get_mouse_abs()
            self.delta = [(mpos[0] - self._lock_position[0] * SORA.WSIZE[0]) / SORA.WSIZE[0], 
                            (mpos[1] - self._lock_position[1] * SORA.WSIZE[1]) / SORA.WSIZE[1]]
            pygame.mouse.set_pos((self._lock_position[0] * SORA.WSIZE[0], self._lock_position[1] * SORA.WSIZE[1]))
        else:
            self.delta = [0, 0]



# timer class
class Timer:
    def __init__(self, limit: float, loop: bool=False):
        self.hash = hash(self)
        self.initial = SORA.get_current_time()
        self.passed = 0
        self.loopcount = 0
        self.limit = limit
        self.loop = loop
        self._active = False
        # signal
        self._signal_register = signal.SignalRegister('timer-finish')
        # register timer
        SORA.ALL_CLOCKS[self.hash] = self

    def update(self):
        """Updates the clock - throws a signal when finished"""
        self.passed += SORA.DELTA
        # to implement sending signals -- when completed!
        # print(self.passed)
        if self.passed > self.limit:
            # -- emit a signal
            self._signal_register.emit_signal()
            self.passed = 0
            self.loopcount += 1
            if not self.loop:
                SORA.deactivate_timer(self)

    def reset_timer(self, time: float = 0):
        """Reset the timer"""
        self.initial = SORA.get_current_time()
        self.passed = 0
        self.loopcount = 0

    def start(self):
        """Start the timer"""
        self._active = True
        SORA.activate_timer(self)
    
    def stop(self):
        """Stop the timer"""
        self._active = False
        SORA.deactivate_timer(self)

    #=== properties
    @property
    def finished_loops(self):
        """Returns the number of loops completed"""
        return self.loopcount
    
    @property
    def time_passed(self):
        """Returns the time passed"""
        return self.passed
    
    @property
    def time_left(self):
        """Returns the time left"""
        return self.limit - self.passed

    @property
    def active(self):
        """Is the timer active?"""
        return self._active

    #=== signals
    def on_finish(self, func):
        """Register a function to be called when the timer finishes"""
        return self._signal_register.add_receiver(func)
