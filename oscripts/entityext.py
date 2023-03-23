import pygame
import numpy as np

from engine.gamesystem import entity
from engine.misc import maths
from engine.handler import scenehandler, eventhandler
from engine import singleton as EGLOB

from . import singleton
from .game import state


# ---------- functions ---------- #

def update_ani_and_hitbox(entity, ani_name, handle=True):
    """This entity must contain an shandler"""
    entity.aregist[ani_name].update()
    entity.sprite = entity.aregist[ani_name].get_frame()
    entity.hitbox = entity.aregist[ani_name].get_hitbox()
    if handle:
        entity.handle_pos = entity.aregist[ani_name].get_frame_data().get_point(singleton.HANDLE_IDENTIFIER)
    entity.p_chunk[0] = int(entity.position.x) // EGLOB.CHUNK_PIX_WIDTH
    entity.p_chunk[1] = int(entity.position.y) // EGLOB.CHUNK_PIX_HEIGHT
    entity.chunk[0] = entity.p_chunk[0]
    entity.chunk[1] = entity.p_chunk[1]
    entity.calculate_rel_hitbox()


def find_idle_mot(MS):
    dx = np.random.random() - .5
    dy = np.random.random() - .5
    return pygame.math.Vector2(dx * MS, dy * MS)


def find_mot_with_weight_vec(vec, weight, MS):
    mot = find_idle_mot(MS)
    # apply linear interpolation
    mot.x = maths.lerp(mot.x, vec.x, weight)
    mot.y = maths.lerp(mot.y, vec.y, weight)
    return mot


# ------------- classes ------------- #


class GameEntity(entity.Entity):
    def __init__(self, entity_name: str, health: int, mana: int):
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
        - position          = vec2
        """
        super().__init__()
        # stats
        self.name = entity_name
        self.health = health
        self.mana = mana
        self.level = 1

        # attacks --------- set to hold attack entity id (for particles)
        self.activeatk = set()
        self.position = pygame.math.Vector2()
        # events
        self.eventhandler = eventhandler.EventStorage()
        # handle (where to hold weapons) position
        self.handle_pos = (0, 0)

    def start(self):
        pass

    def add_active_attack(self, attack):
        self.activeatk.add(attack.id)

    def remove_active_attack(self, attack):
        self.activeatk.remove(attack.id)

    def move_to_position(self):
        """Move rect to position vec"""
        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)

    def kill(self):
        super().kill()


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

    def move_to_position(self):
        """Move rect to position vec"""
        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)
