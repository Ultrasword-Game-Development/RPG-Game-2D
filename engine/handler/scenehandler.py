import pygame
from ..gamesystem import layer

from queue import deque


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
        for layer in self.layers:
            layer.handle(surface)


