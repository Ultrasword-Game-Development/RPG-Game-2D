import pygame
from pygame import math as pgmath, draw as pgdraw

import soragl as SORA
from soragl import animation, base_objects, physics, signal, smath

from scripts.attacks import attacks
from scripts.game import skillhandler

# -------------------------------------------------- #
# skill

# skill data
MR_SKILL_NAME = "Melee-Ranged"
MR_CASTING_TIME = 1
MR_COOLDOWN_TIME = 4
MR_MANA_COST = 0

class MeleeRangeSkill(skillhandler.Skill):
    def __init__(self):
        super().__init__(MR_SKILL_NAME, MR_CASTING_TIME, MR_COOLDOWN_TIME,
                        MR_MANA_COST)

    def activate(self, *args):
        return Fire(args[0])

# -------------------------------------------------- #
# fire class

# animation 
M_ANIM_CAT_FOLDER = "assets/particles/stab"




