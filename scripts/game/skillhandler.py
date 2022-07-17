from engine import clock


class Skill:
    """
    Skill object stores data on skills
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost):
        self.handler = None
        self.parent = None
        self.name = name
        self.cast_time = cast_time
        self.cooldown_time = cooldown_time
        self.mana_cost = mana_cost
    
    def activate(self):
        """Default actiavet method"""
        pass


class OffenseSkill(Skill):
    """
    Offense skills are skills that deal damage
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost, damage):
        super().__init__(name, cast_time, cooldown_time, mana_cost)
        self.damage = damage


class DefensiveSkill(Skill):
    """
    Defensive skills are skills that provide buffs
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost, shield):
        super().__init__(name, cast_time, cooldown_time, mana_cost)
        self.shield = shield

# TODO create more skill types


class Registry:
    """
    A registry for the SkillHandler object
    - allows you to access skills
    """
    def __init__(self, handler):
        """
        Constructor for Registry
        contains:
        - parent            = SkillHandler
        """
        self.parent = handler


class SkillHandler:
    """
    Skillhandler stores skills
    """
    def __init__(self):
        """
        Constructor for SkillHandler
        contains:
        - skills            = {str: Skill}
        """
        self.skills = {}
    
    def add_skill(self, skill):
        """Add skills"""
        self.skills[skill.name] = skill
        skill.handler = self
    
    def remove_skill(self, skill):
        """Remove skills"""
        self.skills.pop(skill.name)

    def get_registry(self):
        """Get a skillhandler registry"""
        return Registry(self)

