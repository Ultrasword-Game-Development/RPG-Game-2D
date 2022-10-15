import pygame

from .. import singleton
from ..handler import scenehandler

E_COUNT = 0

# -------------------------------------------------- #


# entity types
class EntityTypes:
    TYPES = {}

    @classmethod
    def get_entity_type(cls, name):
        """Get an entity class given the name"""
        return cls.TYPES[name] if name in cls.TYPES else None

    @classmethod
    def register_entity_type(cls, name, etype):
        """Register the entity type"""
        cls.TYPES[name] = etype


# entities
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
        if 'name' not in self.__dict__:
            self.name = str(self.id)
        self.dead = False
        self.visible = True
        self.priority = False

        self.sprite = None

        # physics
        self.chunk = [0, 0]
        self.p_chunk = [0, 0]

        self.touching = [False]*4
        self.tiles_area = (0, 0)
        self.position = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.rel_hitbox = pygame.Rect(0, 0, 0, 0)
        self.motion = pygame.math.Vector2(0, 0)
        self.velocity = self.motion

        # parents
        self.layer = None

    def start(self):
        pass

    def update(self):
        pass

    def render(self, surface):
        """Default render"""
        if self.visible and self.sprite:
            surface.blit(self.sprite, self.get_glob_pos())
    
    def debug(self, surface):
        """Debug render"""
        rect = pygame.Rect(self.rel_hitbox.x + singleton.WORLD_OFFSET_X, self.rel_hitbox.y + singleton.WORLD_OFFSET_Y,
                           self.rel_hitbox.w, self.rel_hitbox.h)
        pygame.draw.rect(surface, singleton.DEBUG_COLOR, rect, 1)

    def calculate_rel_hitbox(self):
        """Calculable data for rel_hitbox"""
        self.rel_hitbox.topleft = (self.rect.x + self.hitbox.x, self.rect.y + self.hitbox.y)
        self.rel_hitbox.w = self.hitbox.w
        self.rel_hitbox.h = self.hitbox.h
        self.p_chunk[0] = int(self.rel_hitbox.centerx) // singleton.CHUNK_PIX_WIDTH
        self.p_chunk[1] = int(self.rel_hitbox.centery) // singleton.CHUNK_PIX_HEIGHT
        self.chunk[0] = self.p_chunk[0]
        self.chunk[1] = self.p_chunk[1]

    def kill(self):
        """Kill an entity / remove it from the current state"""
        if self.layer:
            self.layer.handler.remove_entity(self.id)
    
    def get_glob_pos(self):
        """Gets the position with global translation applied"""
        return self.rect.x + singleton.WORLD_OFFSET_X, self.rect.y + singleton.WORLD_OFFSET_Y

    def get_glob_cpos(self):
        """Get the global center position"""
        return self.rel_hitbox.centerx + singleton.WORLD_OFFSET_X, self.rel_hitbox.centery + singleton.WORLD_OFFSET_Y

    def distance_to_other(self, other):
        """Get the distance to another entity"""
        self.calculate_rel_hitbox()
        return pygame.math.Vector2(other.rel_hitbox.x - self.rel_hitbox.x, other.rel_hitbox.y - self.rel_hitbox.y)

    def __eq__(self, other):
        """Check between entities"""
        if type(other) == self.__class__:
            return other.id == self.id
        return self == other

# -------------------------------------------------- #


# static functions
def render_entity_hitbox(entity, window):
    """Render Entity Hitbox"""
    erect = entity.rect
    ehit = entity.hitbox
    pygame.draw.lines(window, singleton.ENTITY_HITBOX_COLOR, True, ((erect.x + ehit.x, erect.y + ehit.y), (erect.x + ehit.right, erect.y + ehit.y), (erect.x + ehit.right, erect.y + ehit.bottom), (erect.x + ehit.x, erect.y + ehit.bottom)))

