import pygame


class World:
    """
    World contains a dict of chunks
    Chunks are objects that contain:
    - tilemap
    - entities
    """
    def __init__(self):
        """
        Constructor for World
        contains:
        - chunks        = dict [str, list]
        """
        self.chunks = {}
    
    def add_chunk(self, chunk):
        """Adds a chunk to the world"""
        self.chunks[chunk.id] = chunk


