from pygame import math as pgmath
from pygame import draw as pgdraw

import soragl as SORA
from soragl import base_objects, smath, physics

from scripts import singleton

# ------------------------------- #
# particle types for game

# TODO -- create particle timer function


def GRAVITY_PARTICLE_CREATE(parent, **kwargs):
    """
    Particles that interact with player -- for testing

    [
        position vector
        velocity vector
        radius (circle)
        gravity
        life (float)
        color (int, int, int)
        id = int
    ]
    """
    return [
        pgmath.Vector2(parent.position.xy),
        pgmath.Vector2(
            smath.normalized_random() * 10, -40 - 70 * smath.np.random.random()
        ),
        1,
        physics.World2D.GRAVITY,
        kwargs["life"],
        kwargs["color"],
        parent.get_new_particle_id(),
    ]


def GRAVITY_PARTICLE_UPDATE(parent, particle):
    """
    Gravity particle update function
    - particles can interact with multiple hitboxes
    - 'hitboxes' array (filled with pygame.Rect objects)
    """
    # check if particle dead
    particle[4] -= SORA.DELTA
    if particle[4] <= 0:
        parent.remove_particle(particle)
        return
    # update velocity
    particle[1] += particle[3] * SORA.DELTA
    # === interact with collision objects registered to be interactable
    # move x
    particle[0].x += particle[1].x * SORA.DELTA
    for hitbox in parent["rects"]:
        if not hitbox.collidepoint(particle[0]):
            continue
        # collided -- check for x movement etc
        if particle[1].x > 0:
            particle[0].x = hitbox.left - 0.2
        elif particle[1].x < 0:
            particle[0].x = hitbox.right + 0.2
        particle[1].x *= -0.3
    # move y
    particle[0].y += particle[1].y * SORA.DELTA
    for hitbox in parent["rects"]:
        if not hitbox.collidepoint(particle[0]):
            continue
        # collided -- check for y movement etc
        if particle[1].y > 0:
            particle[0].y = hitbox.top - 0.2
        elif particle[1].y < 0:
            particle[0].y = hitbox.bottom + 0.2
        particle[1].y *= -0.3
    # === interacting with "ground"
    # clamping position
    if particle[0].y > parent.position.y:
        particle[0].y = parent.position.y
        particle[1].y = -abs(particle[1].y) * 0.3
        particle[1].x *= 0.3

    # render
    pgdraw.circle(SORA.FRAMEBUFFER, particle[5], particle[0], particle[2])


# register functions
physics.ParticleHandler.register_create_function("gravity", GRAVITY_PARTICLE_CREATE)
physics.ParticleHandler.register_update_function("gravity", GRAVITY_PARTICLE_UPDATE)


# gravity particle handler
class GravityParticleHandler(physics.ParticleHandler):
    def __init__(self, **kwargs):
        """Gravity particles handler"""
        super().__init__(args=kwargs, create_func="gravity", update_func="gravity")
        self["rects"] = []

    def update(self):
        """Gravity particle update"""
        print(self["rects"])
        super().update()

    def add_collider(self, rect):
        """Register a collider to be interacted with"""
        self["rects"].append(rect)

    def remove_collider(self, rect):
        """Remove a collider"""
        self["rects"].remove(rect)

    def clear_colliders(self):
        """Clear all colliders"""
        self["rects"].clear()


# ------------------------------------------------------- #
# TODO -- do this
# animated particle
ANIMATED_NAME = "ani_p"


class AnimatedParticle(physics.Entity):
    def __init__(self, registry):
        super().__init__()
        self.aregist = registry
        self.c_sprite = base_objects.AnimatedSprite(0, 0, registry)

    def on_ready(self):
        """Called when entity is ready"""
        # sprite
        self.add_component(self.c_sprite)
        # collision
        self.add_component(base_objects.CollisionComponent(self.c_sprite.area))

    def update(self):
        """Check if dead"""
        if self.aregist.has_finished():
            self.kill()
