from engine import statehandler


class EntityState(statehandler.State):
    def __init__(self, name, parent):
        super().__init__(name)
        self.parent = parent




