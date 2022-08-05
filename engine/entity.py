import pygame

from . import singleton as EGLOB
from . import scenehandler

E_COUNT = 0

class Entity:
    """
    Entity object class
    used for literally everything :)
    """

    def __init__(self):
        """
        Constructor for Entity Class

        - id                = int
        - name              = str
        - sprite            = pygame.Surface
        - motion            = [float, float]
        - dead              = bool
        - visible           = bool
        - rect              = pygame.Rect
        - hitbox            = pygame.Rect
        - rel_hitbox        = pygame.Rect
        - touching          = [bool, bool, bool, bool]
        - chunk             = (int, int)
        - p_chunk           = (int, int)
        - tiles_area        = (int, int)
        
        # for encoding / serializing
        - data [dict]

        # parents
        - group            = Handler
        """
        global E_COUNT
        # give id
        E_COUNT += 1
        self.id = E_COUNT
        self.data = {}
        # define other variables
        self.name = str(self.id)
        self.dead = False
        self.visible = True

        self.sprite = None

        # physics
        self.chunk = (0,0)
        self.p_chunk = (0,0)

        self.touching = [False]*4
        self.tiles_area = (0, 0)
        self.position = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.rel_hitbox = pygame.Rect(0, 0, 0, 0)
        self.motion = pygame.math.Vector2(0, 0)

        # parents
        self.group = None
    
    def update(self):
        pass

    def render(self, surface):
        """Default render"""
        if self.visible and self.sprite:
            surface.blit(self.sprite, self.get_glob_pos())
        
    def calculate_rel_hitbox(self):
        """Calcuale data for rel_hitbox"""
        self.rel_hitbox.topleft = (self.rect.x + self.hitbox.x, self.rect.y + self.hitbox.y)
        self.rel_hitbox.w = self.hitbox.w
        self.rel_hitbox.h = self.hitbox.h

    def kill(self):
        """Kill an entity / remove it from the current state"""
        scenehandler.SceneHandler.CURRENT.handler.remove_entity(self.id)
    
    def get_glob_pos(self):
        """Gets the position with global translation applied"""
        return (self.rect.x + EGLOB.WORLD_OFFSET_X, self.rect.y + EGLOB.WORLD_OFFSET_Y)

    def get_glob_cpos(self):
        """Get the global center position"""
        return (self.rel_hitbox.centerx + EGLOB.WORLD_OFFSET_X, self.rel_hitbox.centery + EGLOB.WORLD_OFFSET_Y)

    def distance_to_other(self, other):
        """Get the distance to another entity"""
        return pygame.math.Vector2(other.rel_hitbox.x - self.rel_hitbox.x, other.rel_hitbox.y - self.rel_hitbox.y)



HITBOX_COLOR = (255, 0, 0)

def render_entity_hitbox(entity, window):
    """Render Entity Hitbox"""
    erect = entity.rect
    ehit = entity.hitbox
    pygame.draw.lines(window, HITBOX_COLOR, True, ((erect.x + ehit.x, erect.y + ehit.y), (erect.x + ehit.right, erect.y + ehit.y), (erect.x + ehit.right, erect.y + ehit.bottom), (erect.x + ehit.x, erect.y + ehit.bottom)))

