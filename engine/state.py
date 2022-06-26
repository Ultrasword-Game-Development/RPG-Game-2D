"""
State Handling file for engine

- State object
- State handling methods
- state queue

"""

from engine import handler, world
from engine.globals import *

from collections import deque
import json
import pickle


STATEQUEUE = deque()
CURRENT = None


class State(handler.Handler, world.World):
    def __init__(self):
        """
        State constructor for states
        
        Extends off both the Handler and World objects
        - allows for entity handling
        - and chunk handling
        
        """
        handler.Handler.__init__(self)
        world.World.__init__(self)
    
    def start(self) -> None:
        """to be overriden by child class - should load the level or whatever it needs to load"""
        pass

    def update(self, dt: float, rel_center: tuple = (0, 0)) -> None:
        """update the state and its handler"""
        self.render_chunks(rel_center)
        self.handle_entities(dt)
    
    def serialize(self) -> dict:
        """
        Serialize the State object

        - stores handler and world data
        - returns dict
        """
        result = {}
        
        # serialize handler
        h = self.serialize_handler()
        # serialize world
        w = self.serialize_world()

        result[STATE_HANDLER_KEY] = h
        result[STATE_WORLD_KEY] = w

        return result
    
    @staticmethod
    def deserialize(data: dict):
        """
        Deserialize the State Object

        - deserialize world and handler
        """
        result = State()

        w = world.World.deserialize_world(data[STATE_WORLD_KEY])
        h = handler.Handler.deserialize_handler(data[STATE_HANDLER_KEY])

        # continue
        # ---
        # set variables
        result.chunks = w.chunks
        result.r_distance = w.r_distance
        result.gravity = w.gravity

        result.p_objects = h.p_objects
        result.objects = h.objects

        return result


def push_state(state: State) -> None:
    """push a new state onto the state stack"""
    global CURRENT
    state.start()
    CURRENT = state
    STATEQUEUE.append(state)


def previous_state(state: State) -> None:
    """go back go back!"""
    STATEQUEUE.pop()
    global CURRENT
    CURRENT = None
    if STATEQUEUE:
        CURRENT = STATEQUEUE[-1]



def pop_state():
    """Pop a state"""
    STATEQUEUE.pop()

