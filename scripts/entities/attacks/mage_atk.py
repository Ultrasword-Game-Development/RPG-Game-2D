
from scripts import singleton
from scripts.entities import fireball



class MageFireBall(fireball.Fire):
    def __init__(self):
        super().__init__()
        
    def update(self):
        self.aregist.update()
        self.sprite = self.aregist.get_frame()
        self.hitbox = self.aregist.get_hitbox()
        self.calculate_rel_hitbox()
        self.aregist.angle = self.motion.angle_to(singleton.DOWN)
        self.aregist.update_angle()

        self.rect.centerx += round(self.motion.x)
        self.rect.centery += round(self.motion.y)
        