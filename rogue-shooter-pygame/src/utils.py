"""Utility functions"""
import pygame
import math
import random


def get_font(size):
    """Safely get a pygame font, returning None if unavailable."""
    try:
        return pygame.font.Font(None, size)
    except Exception:
        return None


def render_text(surf, text, size, pos, color=(255, 255, 255), center=False):
    """Render text to surface, silently skipping if fonts unavailable."""
    font = get_font(size)
    if font is None:
        return
    try:
        img = font.render(str(text), True, color)
        rect = img.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        surf.blit(img, rect)
    except Exception:
        pass


def dist_sq(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy


def dist(x1, y1, x2, y2):
    return math.sqrt(dist_sq(x1, y1, x2, y2))


def angle_between(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def vec_from_angle(angle, length=1):
    return math.cos(angle) * length, math.sin(angle) * length


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))


def random_choice(weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for i, w in enumerate(weights):
        upto += w
        if r <= upto:
            return i
    return len(weights) - 1
