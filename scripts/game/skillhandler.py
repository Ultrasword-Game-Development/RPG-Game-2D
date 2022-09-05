from engine.misc import clock


# ------------------ skills ---------------- #

class Skill:
    """
    Skill object stores data on skills
    """
    def __init__(self, name, cast_time, cooldown_time, mana_cost):
        """
        Constructor for Skill
        contains:
        - parent                = 
        """
        self.parent = None
        self.name = name
        self.cast_time = cast_time
        self.cooldown_time = cooldown_time
        self.mana_cost = mana_cost
    
    def activate(self, *args):
        """Default activate method"""
        pass


# --------------- skill handler --------------- #

class SkillHandler:
    """
    Skillhandler stores skills
    """
    SKILLS = {}
    
    @classmethod
    def add_skill(cls, skill):
        """Add skills"""
        cls.SKILLS[skill.name] = skill
    
    @classmethod
    def remove_skill(cls, skill):
        """Remove skills"""
        cls.SKILLS.pop(skill.name)
    
    @classmethod
    def get_skill(cls, name):
        """Get a skill given the name"""
        return cls.SKILLS.get(name)

# ----------------- skill tree ---------------- #


class SkillTree:
    """
    Store skills --> allows certain registries to access different skills
    
    Static Singleton:
    - stores array of SkillTree objects
    """

    TREES = {}

    @classmethod
    def add_skill_tree(cls, name, base_skill):
        """Add a skill tree"""
        cls.TREES[name] = SkillTree(base_skill, name=name)

    @classmethod
    def get_registry(cls, name):
        """Get a registry for a specific tree"""
        return cls.TREES[name].get_registry()

    # ---------------- class ----------------- #
    def __init__(self, skilltreeloader, name="SkillTree"):
        """
        The Skill Tree limits access to certain skills
        # quite literally a tree
        # there is a starting node
        # starting node leads to branch nodes
        # the path between each node is a limitation
        # --> path acts as a check --> event checks --> prevents entities from accessing certain nodes
        # TODO - LOAD SKILL TREES FROM JSON
        """
        self.name = name
        self.tree_start = skilltreeloader.load_skill_tree()
        self.tree_list = skilltreeloader.get_skills()
    
    def add_skill(self, name):
        """Add skill name to tree_list"""
        self.tree_list.add(name)

    def get_skill(self, name):
        """Get a skill"""
        return SkillHandler.get_skill(name)

    def get_registry(self, ent):
        """Get a skillhandler registry"""
        return Registry(self, ent)


# ----------------- skill node ------------- #

class SkillNode:
    """
    SkillNode stores a skill and a limitation
    """
    def __init__(self, skill, limitation: dict, next_skill=None):
        """
        Constructor for SkillNode
        contains:
        - skill                 = Skill
        - limitation            = dict {str: int}
        - next_skill            = SkillNode
        - parent                = SkillTree
        """
        self.skill = skill
        self.limitation = limitation
        # next skill
        self.left = None
        self.right = None
        self.parent = None
    
    def limit_passed(self, entity):
        """Check if an entity passes the limitations to unlock"""
        # TODO - this hsould be done by checking
        # the level of entity
        # and level of skill / uses of skill by said entity
        print("{}: SkillHandler --> limit pass check to be made".format(__file__.split('\\')[-1]))
        return True


# ---------------- registry ------------------- #

class Registry:
    """
    A registry for the SkillHandler object
    - allows you to access skills
    """
    def __init__(self, skilltree, r_ent):
        """
        Constructor for Registry
        contains:
        - parent            = SkillTree
        - r_ent             = Entity
        - available_skills  = set([str])
        """
        self.parent = skilltree
        self.r_ent = r_ent
        self.available_skills = set()

        self.skills_check()
    
    def add_castable_skill(self, node):
        """Add a skill to the available skills"""
        self.available_skills.add(node.skill.name)
    
    def can_perform_skill(self, name):
        """Check if can perform a certain skill"""
        return name in self.available_skills
    
    def remove_castable_skill(self, node):
        """Remove a castable skill"""
        self.available_skills.remove(node.skill.name)

    def get_skill(self, name):
        """Get a skill"""
        return self.parent.get_skill(name)

    def skills_check(self):
        """Checks for all castable skills by an entity"""
        # check base :)
        if self.parent.tree_start and self.parent.tree_start.skill.name not in self.available_skills:
            if self.parent.tree_start.limit_passed(self.r_ent):
                self.add_castable_skill(self.parent.tree_start)
                self.check_skill_rec(self.parent.tree_start)

    def check_skill_rec(self, skill):
        """Check if can use skill"""
        # if left
        if skill.left and skill.left.skill.name not in self.available_skills:
            if skill.left.limit_passed(self.r_ent):
                self.add_castable_skill(skill.left)
                self.check_skill_rec(skill.left)
        # if right
        if skill.right and skill.right.skill.name not in self.available_skills:
            if skill.right.limit_passed(self.r_end):
                self.add_castable_skill(skill.right)
                self.check_skill_rec(skill.right)

