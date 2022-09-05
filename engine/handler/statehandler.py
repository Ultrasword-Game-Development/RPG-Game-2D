import pygame


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


class StateHandler:
    """
    State handler object for managing different states
    """

    def __init__(self, initial_state = None):
        """
        Constructor for StateHandler
        contains:
        - current_state             = State
        - states                    = dict {str, State}

        Manager function returns a [str] object:
        - manager function is used to determine the best state to use
        - exapmle:
        if x < val:
            return "idle state"

        """
        self.states = {}
        self.current_state = initial_state
    
    def update(self):
        """Update function"""
        self.states[self.current_state].update()

    def add_state(self, state):
        """Add state"""
        self.states[state.name] = state
        state.handler = self
    
    def remove_state(self, name):
        """Remove state"""
        self.states.pop(name)
    
    def set_active_state(self, state: str):
        """Set active state"""
        self.current_state = state
        self.states[self.current_state].start()


