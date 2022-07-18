from engine import entity


class GameEntity(entity.Entity):
    def __init__(self, name: str, health: int, mana: int):
        """
        Constructor for Entity Class - EXTENDED

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
        - chunk             = str "x-y"

        # for encoding / serializing
        - data [dict]

        # parents
        - handler

        # ext
        - health            = int
        - mana              = int
        - level             = float
        """
        super().__init__()
        # stats
        self.name = name
        self.health = health
        self.mana = mana
        self.level = 1

        # attacks --------- set to hold attack entity id (for particles)
        self.activeatk = set()
    
    def add_active_attack(self, attack):
        self.activeatk.add(attack.id)
    
    def remove_active_attack(self, attack):
        self.activeatk.remove(attack.id)
    
    def create_particle(self, pid):
        return [pid, 0, 0, 0, 0, 0, 0]


class NonGameEntity(entity.Entity):
    def __init__(self, name: str, related_entity):
        """
        Constructor for Entity Class - EXTENDED

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
        - chunk             = str "x-y"

        # for encoding / serializing
        - data [dict]

        # parents
        - handler

        # ext
        - rentity           = GameEntity
        """
        super().__init__()
        # stats
        self.name = name
        self.rentity = related_entity

