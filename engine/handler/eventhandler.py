"""
basic event handler system

event is sent to pygame event system:
- event is handled, sent thorugh the system
- event subscribing system ;-;


signal --> emitted
- emitted signal is listed into signal queue
- when signal is updated: loop through layers
- layers handle events - if handled, flag as handled
    - when handling, each layer will call the handle_signal method
    - this will go through each system connected to the signal
    - signals will have a variable that determines if its one target or all targets
- when done update, finish and clear all events from that tick

"""

from ..gamesystem import layer
from queue import deque

class Signal:
    def __init__(self, single=True, *args):
        self.single = single
        self.args = args

        self.handled = False

class Event:
    def __init__(self, name):
        self.name = name
        self.registered = {}
    
    def handle_signal(self):
        pass

class Eventhandler:
    def __init__(self, scene):
        self.events = {}
        self.emitted = deque()

        self.scene = scene

    def emit_signal(self, name):
        """Emits a signal"""
        self.emitted.append(name)
    
    def register_to_signal(self, name, function):
        """Register a function to a signal"""
        if name not in self.registrations:
            self.registrations[name] = Event(name)
        obj = function
        self.registrations[name].append(obj)

    def update(self):
        for s in self.emitted:
            for layer in self.scene.layers:
                layer.handle_signal(s)
                if s.handled:
                    break

# ----------------------------------- #
# access world layers and update thorugh each layer


