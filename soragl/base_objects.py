import soragl as SORA
from soragl import scene, physics, mgl, animation, smath

import random
import math
import glm

from pygame import Rect as pgRect
from pygame import math as pgmath
from pygame import draw as pgdraw
from pygame import transform as pgtrans

"""
1. sprite / rendering components + rendering aspect
2. collision detection component + collision handling aspect

"""

# ------------------------------------------------------------ #
# errors


class MissingComponent(Exception):
    def __init__(self, *args):
        super().__init__(*args)


# ------------------------------------------------------------ #
# base physics objects - entity -- components
# base aspect objects
# ------------------------------------------------------------ #

# ------------------------------ #
# sprite
# NOTE: sprite / animated sprite must be added before renderer!


class MissingSprite(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class Sprite(scene.Component):
    def __init__(self, width: int = 0, height: int = 0, sprite=None, scale_size:tuple=None):
        super().__init__()
        self.width = width
        self.height = height
        # if valid inputs
        if width <= 0 and height <= 0 and not sprite:
            raise NotImplementedError(
                f"Sprite {self} has no width or height or sprite!"
            )
        # if no sprite
        if width <= 0 or height <= 0:
            self._sprite = sprite
            self.width, self.height = self._sprite.get_size()
        else:
            self._sprite = (
                SORA.scale_image(sprite, (width, height))
                if sprite is not None
                else SORA.make_surface(width, height)
            )
        self.hwidth = self.width // 2
        self.hheight = self.height // 2
        # print(self.width, self.height, self._sprite)
        # scaling size
        self.scale_size = scale_size

    @property
    def sprite(self):
        """Get the sprite"""
        return self._sprite

    @sprite.setter
    def sprite(self, new):
        """Set a new sprite"""
        self._sprite = SORA.scale_image(new, (self.width, self.height))

    @property
    def area(self):
        """Get the area"""
        return (self.width, self.height)

    @area.setter
    def area(self, new_area: tuple):
        """set a new area"""
        if len(new_area) != 2:
            raise NotImplementedError(
                f"The area {new_area} is not supported yet! {__file__} {__package__}"
            )
        self.width, self.height = new_area
        self.sprite = SORA.scale_image(self.sprite, (self.width, self.height))


class AnimatedSprite(Sprite):
    def __init__(self, width: int, height: int, registry, scale_size: tuple = None):
        super().__init__(width, height, registry.get_frame(), scale_size=scale_size)
        self._registry = registry

    @property
    def sprite(self):
        """Get the sprite"""
        return self._registry.get_frame()

    @property
    def registry(self):
        """Get the registry"""
        return self._registry

    @registry.setter
    def registry(self, new):
        """Set a new registry"""
        self._registry = new

    @property
    def area(self):
        """Get the area"""
        return self._registry.get_frame().get_size()


class SpriteRenderer(scene.Component):
    def __init__(self):
        super().__init__()
        self._sprite = None

    def on_add(self):
        """On add"""
        # check if parent entity has a sprite component
        # if not self._entity.entity_has_component(Sprite):
        #     raise MissingSprite("Sprite is not an added component")
        self._sprite = self._entity.get_component(Sprite)
        if not self._sprite:
            self._sprite = self._entity.get_component(AnimatedSprite)
        # print(self._sprite)

class SpriteRendererAspect(scene.Aspect):
    def __init__(self):
        super().__init__(SpriteRenderer)
        self.priority = 0

    def handle(self):
        """Render the sprites"""
        for e in self.iterate_entities():
            # get the sprite
            c_sprite = e.get_component(SpriteRenderer)._sprite
            if not c_sprite.sprite:
                continue
            # get the position
            pos = e.position.xy
            # render the sprite
            if c_sprite.scale_size:
                SORA.FRAMEBUFFER.blit(
                    pgtrans.scale(c_sprite.sprite, c_sprite.scale_size),
                    pos - (c_sprite.hwidth, c_sprite.hheight),
                )
                continue
            SORA.FRAMEBUFFER.blit(
                c_sprite.sprite, pos - (c_sprite.hwidth, c_sprite.hheight)
            )


class SpriteRendererAspectDebug(scene.Aspect):
    def __init__(self):
        super().__init__(SpriteRenderer)
        self.priority = 0

    def handle(self):
        """Render the sprites"""
        for e in self.iterate_entities():
            # get the sprite
            c_sprite = e.get_component(SpriteRenderer)._sprite
            # print(c_sprite)
            if not c_sprite or not c_sprite.sprite:
                continue
            # print(c_sprite)
            # render the sprite
            SORA.FRAMEBUFFER.blit(
                c_sprite.sprite, e.position - (c_sprite.hwidth, c_sprite.hheight)
            )
            pgdraw.rect(
                SORA.DEBUGBUFFER,
                (0, 0, 255),
                pgRect(
                    e.position - (c_sprite.hwidth, c_sprite.hheight),
                    c_sprite.sprite.get_size(),
                ),
                1,
            )


# ------------------------------ #
# collision2d


class Collision2DComponent(scene.Component):
    def __init__(self, offset: list = None):
        super().__init__()
        # private
        self._offset = pgmath.Vector2(offset) if offset else pgmath.Vector2(0, 0)
        self._rect = None

    def on_add(self):
        """On add"""
        self._rect = self._entity.rect
        self._rect.center = self._entity.position.xy

    def get_relative_position(self):
        """Get the relative position"""
        return self._offset + self._entity.position

    def get_offset(self):
        """Get the offset"""
        return self._offset

    def get_vertices(self):
        """Iterator for vertices"""
        return [
            self._entity.position
            + self._entity._rect.topleft
            - self._entity._rect.center,
            self._entity.position
            + self._entity._rect.topright
            - self._entity._rect.center,
            self._entity.position
            + self._entity._rect.bottomright
            - self._entity._rect.center,
            self._entity.position
            + self._entity._rect.bottomleft
            - self._entity._rect.center,
        ]


class Collision2DAspect(scene.Aspect):
    def __init__(self):
        super().__init__(Collision2DComponent)
        self.priority = 19
        # private
        self._handler_aspect = (
            None  # to be set after in 'on_add' of the collision2dhandleraspect
        )
        self._tile_map = None

    def on_add(self):
        """On add"""
        self._tile_map = self._world.get_aspect(TileMap)
        if not self._tile_map:
            self._tile_map = self._world.get_aspect(TileMapDebug)
        # if not exist then oh well lmao

    def handle_movement(self, entity):
        """Handle the movement of the entity"""
        """
        move in x
        move in y
        check col both -- resolve col in both
        check surroundings chunks for entities + static objects
        - perform colsion check !!

        update rect pos
        update chunk pos
        """
        # x movement
        entity.position.x += entity.velocity.x * SORA.DELTA
        entity.rect.center = entity.position.xy
        # check for x collisions
        for col in self.iterate_collisions(entity.rect):
            # print(col.rect)
            if entity.velocity.x > 0:
                entity.position.x -= entity.rect.right - col.rect.left
            elif entity.velocity.x < 0:
                entity.position.x += col.rect.right - entity.rect.left
            # update rect
            entity.rect.center = entity.position.xy
        # y movement
        entity.position.y += entity.velocity.y * SORA.DELTA
        entity.rect.center = entity.position.xy
        # check for y collisoins
        for col in self.iterate_collisions(entity.rect):
            if entity.velocity.y > 0:
                entity.position.y -= entity.rect.bottom - col.rect.top
            elif entity.velocity.y < 0:
                entity.position.y += col.rect.bottom - entity.rect.top
            # update rect
            entity.rect.center = entity.position.xy
        # update rect once more
        entity.rect.center = entity.position.xy

        # update chunk position -- if moved to new chunk
        nchunk = [
            int(entity.position.x) // self._world._options["chunkpixw"],
            int(entity.position.y) // self._world._options["chunkpixh"],
        ]
        if nchunk != entity.c_chunk:
            # print("new chunK!!!", nchunk, entity.c_chunk)
            self._world.update_entity_chunk(entity, entity.c_chunk, nchunk)

    def iterate_collisions(self, rect):
        """Detect all collisions that occur with a certain rect"""
        for entity in self.iterate_entities():
            if id(entity.rect) == id(rect) or not entity.static:
                continue
            # check collision
            if rect.colliderect(entity.rect):
                yield entity
        # iterate if there are tilemap
        if not self._tile_map:
            return
        for item in self._tile_map.iterate_active_tiles():
            # print(item)
            if item.rect.colliderect(entity.rect):
                yield item

    def handle(self):
        """Handle Collisions for Collision2D Components"""
        for entity in self.iterate_entities():
            self.handle_movement(entity)


class Collision2DRendererAspectDebug(Collision2DAspect):
    def __init__(self):
        super().__init__()

    def handle(self):
        """Render the collision areas"""
        # print(len(list(self.iterate_entities())))
        for entity in self.iterate_entities():
            self.handle_movement(entity)
            # render debug rect etc
            # print(entity.rect)
            pgdraw.rect(SORA.DEBUGBUFFER, (255, 0, 0), entity.rect, 1)


# ------------------------------ #
# renderable


class Renderable(scene.Component):
    def __init__(self):
        super().__init__()

    def on_add(self):
        if not "renderable" in dir(self._entity):
            raise NotImplementedError(
                self._entity, "doesn't have `renderable` function"
            )


class RenderableAspect(scene.Aspect):
    def __init__(self):
        super().__init__(Renderable)
        self.priority = 2

    def handle(self):
        for e in self.iterate_entities():
            e.renderable()


# ------------------------------ #
# ---


# ------------------------------------------------------------ #
# world component aspects
"""
Contains some aspects -- that act as components
- do not require an entity to run --> simply run on the world
"""
# ------------------------------------------------------------ #

# ------------------------------ #
# tilemap

"""
TODO:
- collision mask
- occlusion mask
"""


class Tile:
    def __init__(self, sprite_path, position, sprite_rect):
        # private
        self._hrect = sprite_rect
        self._position = position
        # public
        self.static = True
        self.position = position
        self.sprite_path = sprite_path

    @property
    def rect(self):
        return pgRect(
            self._position[0] + self._hrect.x,
            self._position[1] + self._hrect.y,
            self._hrect.w,
            self._hrect.h,
        )


class TileMap(scene.Aspect):
    CHUNK_KEY = "tilemap"
    WORLD_KEY = "tilemap"

    def __init__(self):
        super().__init__(None)
        # private
        self._tsize = [0, 0]
        self._chunk_tile_area = [0, 0]
        self._resized_sprites = {}
        self._registered_chunks = set()

    def on_add(self):
        self._tsize = [
            self._world._options["tilepixw"],
            self._world._options["tilepixh"],
        ]
        self._chunk_tile_area = [
            self._world._options["chunktilew"],
            self._world._options["chunktileh"],
        ]

    # === utils
    def load_resized_sprite(self, sprite_path, rect=None):
        """Get a resized sprite"""
        if sprite_path not in self._resized_sprites:
            self._resized_sprites[sprite_path] = (
                pgtrans.scale(SORA.load_image(sprite_path), self._tsize),
                rect if rect else pgRect(0, 0, 0, 0),
            )
        return self._resized_sprites[sprite_path]

    def set_sprite_data(self, sprite_path, rect):
        """Set sprite data for a sprite"""
        if sprite_path in self._resized_sprites:
            rref = self._resized_sprites[sprite_path][1]
            rref.topleft = rect.topleft
            rref.w, rref.h = rect.w, rect.h
        else:
            self.load_resized_sprite(sprite_path, rect)

    # === tiles
    def add_tile_to_chunk(self, cx: int, cy: int, sprite_path: str, tx: int, ty: int):
        """Add a tile to a chunk"""
        # literally a dict
        chunk = self._world.get_chunk(
            cx + tx // self._chunk_tile_area[0], (cy + ty // self._chunk_tile_area[1])
        )
        # if not registered already -- do so now
        if not self.CHUNK_KEY in chunk._dev:
            chunk._dev[self.CHUNK_KEY] = {}
        # add tile
        tx, ty = smath.__mod__(tx, self._chunk_tile_area[0]), smath.__mod__(
            ty, self._chunk_tile_area[1]
        )
        sprite_data = self.load_resized_sprite(sprite_path)
        chunk._dev[self.CHUNK_KEY][self.get_tile_hash(tx, ty)] = Tile(
            sprite_path,
            (tx * self._tsize[0] + chunk.rect.x, ty * self._tsize[1] + chunk.rect.y),
            self._resized_sprites[sprite_path][1],
        )
        self._registered_chunks.add(hash(chunk))
        # print(chunk._dev[self.CHUNK_KEY][self.get_tile_hash(tx, ty)])

    def add_tile_global(self, sprite_path: str, tx: int, ty: int):
        """Add a tile to the world"""
        cx, cy = tx // self._chunk_tile_area[0], ty // self._chunk_tile_area[1]
        tx, ty = smath.__mod__(tx, self._chunk_tile_area[0]), smath.__mod__(
            ty, self._chunk_tile_area[1]
        )
        self.add_tile_to_chunk(cx, cy, sprite_path, tx, ty)

    def get_tile_hash(self, tx: int, ty: int):
        """Get a tile hash"""
        return f"{int(tx)}|{int(ty)}"

    def iterate_active_tiles(self):
        """iterate t hrough all the active tils"""
        for cid in self._world._active_chunks:
            if not cid in self._registered_chunks:
                continue
            for item in self._world._chunks[cid]._dev[self.CHUNK_KEY].values():
                yield item

    # === rendering
    def handle(self):
        """Handle the rendering of the tilemap"""
        for item in self.iterate_active_tiles():
            SORA.FRAMEBUFFER.blit(self._resized_sprites[item.sprite_path][0], item.rect)


class TileMapDebug(TileMap):
    def __init__(self):
        super().__init__()

    def handle(self):
        """Handle the rendering of the tilemap"""
        for item in self.iterate_active_tiles():
            SORA.FRAMEBUFFER.blit(self._resized_sprites[item.sprite_path][0], item.rect)
            # debug render rect
            r = self._resized_sprites[item.sprite_path]
            # if r.w == 0 or r.h == 0: continue
            # print((r.x + item[0], r.y + item[0], r.w, r.h))
            pgdraw.rect(SORA.DEBUGBUFFER, (0, 0, 255), item.rect, 1)


# ------------------------------------------------------------ #
# particle system
"""
Particle systems are very cool
- here are some standard objects!
"""
# ------------------------------------------------------------ #

# ------------------------------ #
# square particle


def create_square_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [
        parent.position.xy,
        kwargs["vel"]
        if "vel" in kwargs
        else pgmath.Vector2(
            (random.random() - 0.5) * 100, (random.random() - 0.5) * 100
        ),
        0,  # angle,
        kwargs["angv"] if "angv" in kwargs else (random.random() - 0.5) * 100,
        list(kwargs["color"]) if "color" in kwargs else [0, 0, 255],
        kwargs["life"] if "life" in kwargs else 1.0,
        (
            physics.World2D.RIGHT * r,
            physics.World2D.UP * r,
            physics.World2D.LEFT * r,
            physics.World2D.DOWN * r,
        ),  # points
        parent.get_new_particle_id(),
    ]


def update_square_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= SORA.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = int(math.sin(SORA.ENGINE_UPTIME) * 127 + 127)
    particle[4][1] = int(math.cos(SORA.ENGINE_UPTIME) * 127 + 127)
    particle[4][2] = int(math.sin(particle[0].x) * 127 + 127)
    # just spin + move in random direction
    particle[0] += particle[1] * SORA.DELTA
    particle[2] += particle[3] * SORA.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(SORA.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("square", create_square_particle)
physics.ParticleHandler.register_update_function("square", update_square_particle)

# ------------------------------ #
# triangle particles


def create_triangle_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [
        parent.position.xy,
        kwargs["vel"]
        if "vel" in kwargs
        else pgmath.Vector2(
            (random.random() - 0.5) * 100, (random.random() - 0.5) * 100
        ),
        0,  # angle,
        kwargs["angv"] if "angv" in kwargs else (random.random() - 0.5) * 1000,
        list(kwargs["color"]) if "color" in kwargs else [0, 0, 255],
        kwargs["life"] if "life" in kwargs else 1.0,
        (
            physics.World2D.RIGHT * r,
            physics.World2D.RIGHT.rotate(120) * r,
            physics.World2D.RIGHT.rotate(240) * r,
        ),  # points
        parent.get_new_particle_id(),
    ]


def update_triangle_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= SORA.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = int(math.sin(SORA.ENGINE_UPTIME) * 127 + 127)
    particle[4][1] = int(math.cos(SORA.ENGINE_UPTIME) * 127 + 127)
    particle[4][2] = int(math.sin(particle[0].x) * 127 + 127)
    # just spin + move in random direction
    particle[0] += particle[1] * SORA.DELTA
    particle[2] += particle[3] * SORA.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(SORA.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("triangle", create_triangle_particle)
physics.ParticleHandler.register_update_function("triangle", update_triangle_particle)

# ------------------------------ #
# triangle particles

__custom_shape = [
    pgmath.Vector2(0, -1),
    pgmath.Vector2(1, 0),
    pgmath.Vector2(0.9, 0.15),
    pgmath.Vector2(0.8, 0.4),
    pgmath.Vector2(0.6, 0.7),
    pgmath.Vector2(0.5, 0.65),
    pgmath.Vector2(0.4, 0.5),
    pgmath.Vector2(0.2, 0.4),
    pgmath.Vector2(0, 0),
    pgmath.Vector2(-0.2, 0.4),
    pgmath.Vector2(-0.4, 0.5),
    pgmath.Vector2(-0.5, 0.65),
    pgmath.Vector2(-0.6, 0.7),
    pgmath.Vector2(-0.8, 0.4),
    pgmath.Vector2(-0.9, 0.15),
    pgmath.Vector2(-1, 0),
]


def create_custom_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [
        parent.position.xy,
        kwargs["vel"]
        if "vel" in kwargs
        else pgmath.Vector2(
            (random.random() - 0.5) * 100, (random.random() - 0.5) * 100
        ),
        0,  # angle,
        kwargs["angv"] if "angv" in kwargs else (random.random() - 0.5) * 1000,
        list(kwargs["color"]) if "color" in kwargs else [255, 192, 203],
        kwargs["life"] if "life" in kwargs else 1.0,
        tuple([_ * r for _ in __custom_shape]),  # points
        parent.get_new_particle_id(),
    ]


def update_custom_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= SORA.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = 255 - abs(int(math.sin(particle[0].y) * 100))
    particle[4][1] = abs(int(math.cos(SORA.ENGINE_UPTIME) * 129))
    particle[4][2] = 200 - abs(int(math.sin(particle[0].x) * 40))
    # just spin + move in random direction
    particle[0] += particle[1] * SORA.DELTA
    particle[2] += particle[3] * SORA.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(SORA.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("custom", create_custom_particle)
physics.ParticleHandler.register_update_function("custom", update_custom_particle)


# ------------------------------------------------------------ #
# 3D / 2D cameras!
"""
For use in opengl based applications / games! -- not pygame 2D
- whenever you want to render something, you need to use the camera's view matrix
"""
# ------------------------------------------------------------ #


class OrthoCamera(mgl.Camera):
    def __init__(self, pos, front, up):
        super().__init__(pos, front, up, (0, 0, 0))
        # private
        self._view = self.calculate_view_matrix(self._position, self._front, self._up)
        self._proj = self.calculate_ortho_matrix(
            0, SORA.SCREEN_WIDTH, SORA.SCREEN_HEIGHT, 0, -1, 1
        )


class FrustCamera(mgl.Camera):
    def __init__(
        self,
        position: pgmath.Vector3,
        target: pgmath.Vector3,
        fov: float,
        aspect: float,
        near: float = 0.1,
        far: float = 1000.0,
    ):
        super().__init__(position, target, physics.World3D.UP, (0, 0, 0))
        # private
        self._near = near
        self._far = far
        self._fov = fov
        self._aspect = aspect

        # public
        # view changes -- translation + rotation + scaling
        self._view = self.calculate_view_matrix()
        # proj doesnt change too often -- fov + aspect + near + far
        self._proj = glm.perspective(
            glm.radians(self._fov), self._aspect, self._near, self._far
        )


print("More objects to be added! base_objects.py")
