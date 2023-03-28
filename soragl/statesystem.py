import pygame
from soragl import scene, misc

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
    
    def start(self):
        """Start function"""
        pass

    def update(self):
        """Update function"""
        pass


# -------------------------------------------------- #
# state handler
class StateHandler(scene.Component, misc.Dictionary):
    """
    A component class that wraps up the entity state system
    """
    def __init__(self):
        """Initialzie the Statehandler object"""
        super(scene.Component, self).__init__()
        super(misc.Dictionary, self).__init__()
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
        self.states[self._current].start()


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
            if not c_shandler._current:
                continue
            c_shandler.states[c_shandler._current].update()

