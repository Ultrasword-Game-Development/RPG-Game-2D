import pygame
from .. import singleton
from . import chunk
from ..handler import handler


class World:
    """
    World contains a dict of chunks
    Chunks are objects that contain:
    - tilemap
    - entities
    """

    def __init__(self, layer):
        """
        Constructor for World
        contains:
        - chunks        = dict [str, list]
        """
        self.layer = layer
        self.scene = layer.scene
        self.chunks = {}

        # -------------------------------------------------- #
        # environment objects
        self.env = handler.Handler(self.layer)

    def add_chunk(self, chunk):
        """Adds a chunk to the world"""
        self.chunks[chunk.id] = chunk
        chunk.world = self

    def get_chunk(self, x: int, y: int):
        """Get a chunk"""
        key = f"{x}-{y}"
        if key not in self.chunks:
            self.chunks[key] = chunk.Chunk(x, y, self)
        return self.chunks[key]

    def handle_chunks(self, surface, render_dis: list = (0, 0)):
        """Handles rendering of chunks"""
        # update entiyt handler
        self.env.handle_changes()
        # update chunks and entities
        for ix in range(self.layer.camera.chunkpos[0] - render_dis[0],
                        self.layer.camera.chunkpos[0] + render_dis[0] + 1):
            for iy in range(self.layer.camera.chunkpos[1] - render_dis[1],
                            self.layer.camera.chunkpos[1] + render_dis[1] + 1):
                # print(ix, iy)
                c = self.get_chunk(ix, iy)
                if not self.layer.camera.viewport.colliderect(c.area_rect):
                    continue
                # update chunk
                c.handle(surface)

    def debug_handle_chunks(self, surface, render_dis: list = (0, 0)):
        """Debug Handles Rendering of Chunks"""
        self.handle_chunks(surface, render_dis)
        for ix in range(self.layer.camera.chunkpos[0] - render_dis[0],
                        self.layer.camera.chunkpos[0] + render_dis[0] + 1):
            for iy in range(self.layer.camera.chunkpos[1] - render_dis[1],
                            self.layer.camera.chunkpos[1] + render_dis[1] + 1):
                c = self.get_chunk(ix, iy)
                rect = pygame.Rect(c.area_rect.x + singleton.WORLD_OFFSET_X, c.area_rect.y + singleton.WORLD_OFFSET_Y,
                                   c.area_rect.w, c.area_rect.h)
                pygame.draw.rect(surface, singleton.DEBUG_COLOR, rect, 1)

    def move_entity(self, entity):
        """Move an entity through the chunk"""
        # find range of intercepting tiles
        intercept = pygame.Rect((entity.rect.x // singleton.TILE_WIDTH - 1, entity.rect.y // singleton.TILE_HEIGHT - 1),
                                entity.tiles_area)
        # move x\
        entity.position.x += entity.motion.x
        # check for collisions with tilemap
        # nothign yet
        # move y
        entity.position.y += entity.motion.y
        # check for collisions with tile-map

        entity.chunk = [int(entity.position.x) // singleton.CHUNK_PIX_WIDTH,
                        int(entity.position.y) // singleton.CHUNK_PIX_HEIGHT]
        if entity.chunk != entity.p_chunk:
            self.get_chunk(entity.p_chunk[0], entity.p_chunk[1]).remove_entity(entity)
            entity.p_chunk = entity.chunk
            self.get_chunk(entity.chunk[0], entity.chunk[1]).add_entity(entity)
        # print(entity.name, entity.chunk)

    def find_nearby_entities(self, cpos: tuple, crange: int):
        """Searches nearby chunks for entities - is an iterable"""
        for ix in range(cpos[0] - crange, cpos[0] + crange + 1):
            for iy in range(cpos[1] - crange, cpos[1] + crange + 1):
                c = self.get_chunk(ix, iy)
                # find entities in chunk
                for e in c.entities:
                    if e in self.layer.handler.entities:
                        yield self.layer.handler.entity_buffer[e]

    def add_env_obj(self, obj):
        """Add an object to world"""
        self.env.add_entity(obj)
        # find chunk
        c = self.get_chunk(obj.chunk[0], obj.chunk[1])
        if c: c.add_env_obj(obj)

    def remove_env_obj(self, obj):
        """Remove env obj"""
        self.env.remove_entity(obj)
