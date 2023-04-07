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
        return MeleeRange(args[0])

# -------------------------------------------------- #
# fire class

# animation 
M_ANIM_CAT = "assets/particles/melee_attack.json"
M_IDLE_ANIM = "seq"

animation.Category.load_category(M_ANIM_CAT)
M_ANIM_CACHE = animation.Category.get_category_framedata(M_ANIM_CAT)

class MeleeRange(attacks.Attack):
    def __init__(self, sender: "Entity"):
        super().__init__(sender.position.xy, M_ANIM_CACHE[M_IDLE_ANIM].get_registry(), sender=sender)
        # private
        # self._phandler = physics.ParticleHandler()

    def on_ready(self):
        self.area = (4, 4)
        super().on_ready()
        # self.add_link(self._phandler)

    def update(self):
        super().update()
        # self._phandler.position = self.position
        # kill check
        if self.aregist.finished_loops():
            self.kill()

# ------------- setup ----------- #
skillhandler.SkillHandler.add_skill(MeleeRangeSkill())


