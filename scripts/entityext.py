from engine import entity


class GameEntity(entity.Entity):
    def __init__(self, name: str, health: int, mana: int):
        super().__init__()
        self.name = name
        self.health = health
        self.mana = mana
        self.level = 1

