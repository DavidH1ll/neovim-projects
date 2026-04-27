"""Pickup items"""
import pygame
from settings import *


class Pickup(pygame.sprite.Sprite):
    def __init__(self, game, x, y, pickup_type):
        super().__init__()
        self.game = game
        self.pickup_type = pickup_type
        
        names = {
            PICKUP_COIN: 'pickup_coin',
            PICKUP_HEALTH: 'pickup_health',
            PICKUP_GUN: 'pickup_gun',
        }
        name = names.get(pickup_type, 'pickup_coin')
        self.image = game.assets.get_sprite(name, 0)
        if self.image is None:
            self.image = pygame.Surface((8, 8))
            colors = {PICKUP_COIN: (255, 215, 0), PICKUP_HEALTH: (255, 0, 0), PICKUP_GUN: (0, 255, 0)}
            self.image.fill(colors.get(pickup_type, (255, 255, 255)))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_timer = 0
    
    def update(self):
        self.bob_timer += 1
        # Check player collision
        if self.game.player and self.rect.colliderect(self.game.player.hitbox):
            self.collect()
    
    def collect(self):
        if self.pickup_type == PICKUP_COIN:
            self.game.current_coins += 1
            self.game.audio.play_sfx('pickup_coin', 0.3)
        elif self.pickup_type == PICKUP_HEALTH:
            if self.game.player:
                self.game.player.heal(1)
        elif self.pickup_type == PICKUP_GUN:
            self.game.audio.play_sfx('pickup_gun', 0.3)
        
        self.kill()
    
    def draw(self, surf, cx, cy):
        offset_y = int(math.sin(self.bob_timer * 0.1) * 2)
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy + offset_y))


import math
