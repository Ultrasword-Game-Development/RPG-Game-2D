import pygame


def make_pygame_rect(x, y, w, h):
    """Make a pygame rect and return it"""
    return pygame.Rect(x, y, w, h)


def get_frames_per_second(delta_time: float) -> float:
    """Get the fps"""
    return 1 / delta_time if delta_time > 0 else 0
