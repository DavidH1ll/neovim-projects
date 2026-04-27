"""Breakable objects"""
import pygame
import random
from settings import *


class Breakable(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        sprites = game.assets.get_sprites('breakable')
        self.image = sprites[0] if sprites else pygame.Surface((16, 16))
        if self.image is None:
            self.image = pygame.Surface((16, 16))
            self.image.fill((139, 90, 43))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-4, -4)
    
    def update(self):
        # Check player dash collision
        if self.game.player and self.game.player.is_dashing:
            if self.hitbox.colliderect(self.game.player.hitbox):
                self.smash()
                return
        
        # Check bullet collision is handled in bullet update
    
    def smash(self):
        self.game.audio.play_sfx('box_breaking', 0.3)
        
        # Spawn broken pieces
        pieces = self.game.assets.get_sprites('broken_piece')
        if pieces:
            self.game.particles.spawn_broken_pieces(self.rect.centerx, self.rect.centery, pieces, 4)
        
        # Drop item
        if random.random() < 0.4:
            drop_type = random.choice([PICKUP_COIN, PICKUP_COIN, PICKUP_HEALTH])
            self.game.spawn_pickup(self.rect.centerx, self.rect.centery, drop_type)
        
        self.kill()
    
    def draw(self, surf, cx, cy):
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))
