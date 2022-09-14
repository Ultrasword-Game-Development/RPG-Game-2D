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
from . import scenehandler

from queue import deque


class Event:
    def __init__(self, name, data: dict):
        self.name = name
        self.data = data


class FunctionWrapper:
    COUNTER = 0

    @classmethod
    def get_id(cls):
        cls.COUNTER += 1
        return cls.COUNTER

    def __init__(self, ref, func):
        self.ref = ref
        self.func = func
        self.fid = FunctionWrapper.get_id()

    def __eq__(self, other):
        return self.fid == other.fid

# -------------------------------------------------- #
# event handler


class Eventhandler:
    EMITTED = deque()
    EVENTS = {}

    @classmethod
    def emit_signal(cls, event: Event):
        """Emits a signal"""
        cls.EMITTED.append(event)

    @classmethod
    def register_to_signal(cls, name, function):
        """Register a function to a signal"""
        if name not in cls.EVENTS:
            # create a new registry Event
            cls.EVENTS[name] = []
        wrapper = FunctionWrapper(name, function)
        cls.EVENTS[name].append(wrapper)
        return wrapper

    @classmethod
    def remove_signal(cls, name):
        cls.EVENTS.pop(name)

    @classmethod
    def unregister_from_signal(cls, wrapper):
        """Unregister a function from a signal"""
        cls.EVENTS[wrapper.ref].remove(wrapper)

    @classmethod
    def update(cls):
        for s in cls.EMITTED:
            for wrap in cls.EVENTS[s.name]:
                wrap.func(s)
        cls.EMITTED.clear()


# -------------------------------------------------- #
# event storage - stored within entities


class EventStorage:
    def __init__(self):
        self.wrappers = {}

    def emit_signal(self, event):
        """Emit a Signal"""
        Eventhandler.emit_signal(event)

    def register_to_signal(self, signal: str, function):
        """Register easily"""
        wrap = Eventhandler.register_to_signal(signal, function)
        self.wrappers[signal] = wrap

    def unregister_from_signal(self, signal: str):
        """Unregister easily"""
        Eventhandler.unregister_from_signal(self.wrappers[signal])


# ----------------------------------- #
# access world layers and update thorugh each layer
