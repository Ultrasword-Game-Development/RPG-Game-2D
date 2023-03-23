import json
from .game import skillhandler


# ------------ skill types ----------- #

class OffenseSkill(skillhandler.Skill):
    """
    Offense skills are skills that deal damage
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost, damage):
        super().__init__(name, cast_time, cooldown_time, mana_cost)
        self.damage = damage


class DefensiveSkill(skillhandler.Skill):
    """
    Defensive skills are skills that provide buffs
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost, shield):
        super().__init__(name, cast_time, cooldown_time, mana_cost)
        self.shield = shield


# TODO create more skill types


# -------------- skill ext ---------------- #


class SkillTreeLoader:
    """
    SkillTreeLoader loads skill trees from json files
    """
    def __init__(self, filepath):
        self.filepath = filepath
        with open(self.filepath, 'r') as file:
            self.filedata = json.load(file)
            file.close()
        self.skills = set()

    def load_skill_tree(self):
        """Load skills from a json file"""
        return self.parse_skill_tree("base")
        
    def parse_skill_tree(self, name):
        """Parse a skill tree"""
        nodename = self.filedata[name]
        nodebranch = self.filedata[nodename]["branch"]
        nodelim = self.filedata[nodename]["limitation"]
        nodeskill = skillhandler.SkillHandler.get_skill(nodename)
        result = skillhandler.SkillNode(nodeskill, nodelim)
        self.skills.add(nodename)
        # left branch
        if nodebranch[0]:
            result.left = self.parse_skill_tree(nodebranch[0])
        # right branch
        if nodebranch[1]:
            result.right = self.parse_skill_tree(nodebranch[1])
        return result
    
    def get_skills(self):
        """Get the skills set"""
        return self.skills


