import pygame

E_COUNT = 0

class Entity:
    """
    Entity object class
    used for literally everything :)
    """

    def __init__(self):
        """
        Constructor for Entity Class

        - id [int]
        - name [str]
        - sprite [pygame.Surface]
        - motion [float, float]
        - dead [bool]
        
        # for encoding / serializing
        - data [dict]

        # parents
        - handler
        """
        # give id
        E_COUNT += 1
        self.id = E_COUNT
        # define other variables
        self.name = str(self.id)
        self.dead = False

        self.sprite = None

        # physics
        self.motion = [0, 0]
        self.hitbox = pygame.Rect()

        # parents
        self.group = None

