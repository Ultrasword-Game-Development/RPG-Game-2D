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
    
    def update(self):
        """Update function"""
        pass


class StateHandler:
    """
    State handler object for managing different states
    """

    def __init__(self):
        """
        Constructor for StateHandler
        contains:
        - manager_func              = str func, no params
        - handler_data              = dict {}

        - states                    = dict {str, State}

        Manager function returns a [str] object:
        - manager function is used to determine the best state to use
        - exapmle:
        if x < val:
            return "idle state"

        """
        self.manager_func = lambda : print(self.states)
        self.handler_data = {}
        self.states = {}
    
    def update(self):
        """Update function"""
        self.states[self.manager_func(self)].update()
    
    def add_state(self, state):
        """Add state"""
        self.states[state.name] = state
        state.handler = self
    
    def remove_state(self, name):
        """Remove state"""
        self.states.pop(name)
    
    def set_data(self, name, data):
        """Add a data value"""
        self.handler_data[name] = data
    
    def set_management_func(self, func):
        """Set the management func"""
        self.manager_func = func


