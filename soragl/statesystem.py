import pygame
from soragl import scene

# -------------------------------------------------- #
# state

class State:
    """
    State class for managing different states in the state handler
    """
    def __init__(self, name):
        """
        Constructor for State object
        contains:
        - name              = str
        - handler           = StateHandler
        """
        self.name = name
        self.handler = None
    
    def on_ready(self):
        """Start function"""
        pass
    
    def update(self):
        """Update function"""
        pass


# -------------------------------------------------- #
# state handler
class StateHandler(scene.Component):
    """
    A component class that wraps up the entity state system
    """
    def __init__(self):
        """Initialzie the Statehandler object"""
        self.states = {}
        self._current = None
    
    def add_state(self, state):
        """Add a state tot he handler"""
        self.states[state.name] = state
        state.handler = self
    
    def remove_state(self, name: str):
        """Remove a state from the handler"""
        del self.states[name]
    
    #=== properties
    @property
    def current(self):
        """Get the current state"""
        return self._current

    @current.setter
    def current(self, new):
        """Update the current state"""
        self._current = new
        self.states[self._current].on_ready()


# -------------------------------------------------- #
# state handler aspect
class StateHandlerAspect(scene.Aspect):
    """
    An aspect that handles the updating of Statehandelr components
    """
    def __init__(self):
        super().__init__(StateHandler)
    
    def handle(self):
        """Handles the components"""
        for ent in self.iterate_entities():
            c_shandler = ent.get_component(StateHandler)
            c_handler.states[c_hander._current].update()


# -------------------------------------------------- #
# entity state
class EntityState(State):
    def __init__(self, name, entity):
        super().__init__(name)
        self.entity = entity



