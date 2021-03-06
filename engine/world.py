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
    
    def get_chunk(self, x: int, y: int):
        """Get a chunk"""
        return self.chunks.get(f"{x}-{y}")
    
    def handle_chunks(self, surface):
        """Handles rendering of chunks"""
        # print("handling chunks")
        # TODO - create system for rendering chunks
        pass


