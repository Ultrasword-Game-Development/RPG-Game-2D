import pygame
from . import handler, world

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
        self.handler = handler.Handler(self)
        self.world = world.World(self)

