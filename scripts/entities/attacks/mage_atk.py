
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
        self.phandler.update()

        self.distance_travelled += self.motion.magnitude()
        if self.distance_travelled > self.max_distance:
            self.kill()

        self.position[0] += self.motion.x
        self.position[1] += self.motion.y
        self.rect.center = list(map(int, self.position))