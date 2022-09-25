import pygame
from ..gamesystem import layer
from . import statehandler

from queue import deque


# -------------------------------------------------- #
# scenehandler class

class SceneHandler:
    """
    SceneHandler for handling a variety of scenes
    - a STATIC class meant to hold a scene queue
    """
    CURRENT = None
    QUEUE = deque()

    @staticmethod
    def push_state(scene):
        """Push a new scene onto the queue"""
        SceneHandler.QUEUE.append(scene)
        SceneHandler.CURRENT = scene

    @staticmethod
    def pop_state():
        """Pop the last state off the queue"""
        SceneHandler.QUEUE.pop()
        SceneHandler.CURRENT = None
        if SceneHandler.QUEUE:
            SceneHandler.CURRENT = SceneHandler.QUEUE[-1]

    @staticmethod
    def clean():
        """Cleans all scenes from queue"""
        while SceneHandler.QUEUE:
            scene = SceneHandler.QUEUE.pop()
            scene.clean()


# -------------------------------------------------- #
# scene state class

class SceneState(statehandler.State):
    # -------------------------------------------------- #
    # class vars
    NAME = "state"

    # -------------------------------------------------- #
    def __init__(self, scene, name="state"):
        super().__init__(name)
        self.scene = scene

    def update_scene(self, surface):
        for layer in self.scene.layers:
            layer.handle(surface)


# -------------------------------------------------- #
# scene class

class Scene:
    """
    Scene for handling different gamestates within an active game
    """

    def __init__(self):
        """
        Constructor for GameState
        contains:
        - handler               = handler.Handler()
        - world                 = world.World()
        """
        self.layers = []
        self.data = {}
        self.state = statehandler.StateHandler(SceneState.NAME)
        self.state.add_state(SceneState(self))

    def add_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data[key]

    def add_layer(self):
        self.layers.append(layer.Layer(self))
        return self.layers[-1]

    def get_layer(self, index):
        return self.layers[index]

    def update(self, surface):
        # implement scene state handler
        self.state.states[self.state.current_state].update_scene(surface)
