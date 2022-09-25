from scripts import singleton, entityext


# ----------------------------------- #
# ambience system

class AmbienceSystem:
    def __init__(self):
        self.layer = None

    def handle(self, surface):
        pass

    def debug(self, surface):
        pass

    def affect_function(self, affected):
        """Function for interacting with in world objects"""
        pass


# ----------------------------------- #
# ambience handler

class Ambience(entityext.NonGameEntity):
    # ----------------------------------- #
    # constants

    # ----------------------------------- #
    def __init__(self):
        super().__init__("ambience", None)
        # ----------------------------------- #
        # systems to handle
        self.systems = []

    def update(self):
        # screw the update function :)
        pass

    def render(self, surface):
        # update everything
        for system in self.systems:
            system.handle(surface)

    def debug(self, surface):
        for system in self.systems:
            system.debug(surface)

    def add_system(self, system):
        """Add a system"""
        system.layer = self.layer
        self.systems.append(system)

    def remove_system(self, system):
        """Remove a system"""
        self.systems.remove(system)



