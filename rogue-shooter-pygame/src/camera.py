"""Camera system"""
import pygame
from settings import NATIVE_W, NATIVE_H


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.speed = 8
    
    def snap_to_room(self, room):
        self.target_x = -(room.x + room.width // 2) + NATIVE_W // 2
        self.target_y = -(room.y + room.height // 2) + NATIVE_H // 2
        self.x = self.target_x
        self.y = self.target_y
    
    def move_to_room(self, room):
        self.target_x = -(room.x + room.width // 2) + NATIVE_W // 2
        self.target_y = -(room.y + room.height // 2) + NATIVE_H // 2
    
    def get_offset(self):
        # Smooth follow
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * 0.15
        
        return int(self.x), int(self.y)
    
    def can_see(self, rect):
        cx, cy = self.get_offset()
        view_rect = pygame.Rect(-cx, -cy, NATIVE_W, NATIVE_H)
        return view_rect.colliderect(rect)
