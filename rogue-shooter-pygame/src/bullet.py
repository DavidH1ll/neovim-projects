"""Bullet classes"""
import pygame
import math
from settings import NATIVE_W, NATIVE_H


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle, speed):
        super().__init__()
        self.game = game
        self.image = game.assets.get_sprite('bullet_player', 0)
        if self.image is None:
            self.image = pygame.Surface((4, 4))
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 120
        self.damage = 50
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # Check wall collisions
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                self._impact()
                return
        
        for door in self.game.doors:
            if door.is_closed and self.rect.colliderect(door.rect):
                self._impact()
                return
        
        # Check enemy collisions
        for enemy in self.game.enemies:
            if self.rect.colliderect(enemy.hitbox):
                enemy.take_damage(self.damage)
                self.game.particles.spawn_hit(self.rect.centerx, self.rect.centery, (255, 255, 200), 5)
                self.kill()
                return
        
        # Check boss collision
        if self.game.boss and self.rect.colliderect(self.game.boss.hitbox):
            self.game.boss.take_damage(self.damage)
            self.game.particles.spawn_hit(self.rect.centerx, self.rect.centery, (255, 100, 100), 5)
            self.kill()
            return
        
        # Check breakables
        for breakable in self.game.breakables:
            if self.rect.colliderect(breakable.rect):
                breakable.smash()
                self._impact()
                return
        
        # Out of bounds
        if self.x < -500 or self.x > 5000 or self.y < -500 or self.y > 5000:
            self.kill()
    
    def _impact(self):
        self.game.audio.play_sfx('impact', 0.3)
        self.game.particles.spawn_hit(self.rect.centerx, self.rect.centery, (255, 255, 200), 3)
        self.kill()
    
    def draw(self, surf, cx, cy):
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, target_x, target_y, speed=2):
        super().__init__()
        self.game = game
        self.image = game.assets.get_sprite('bullet_enemy', 0)
        if self.image is None:
            self.image = pygame.Surface((4, 4))
            self.image.fill((255, 50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
        else:
            self.vx = 0
            self.vy = 0
        
        self.lifetime = 180
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # Check wall collisions
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                self.kill()
                return
        
        for door in self.game.doors:
            if door.is_closed and self.rect.colliderect(door.rect):
                self.kill()
                return
        
        # Check player collision
        if self.game.player and self.rect.colliderect(self.game.player.hitbox):
            self.game.player.take_damage(1)
            self.kill()
            return
    
    def draw(self, surf, cx, cy):
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))


class BossBullet(EnemyBullet):
    def __init__(self, game, x, y, target_x, target_y, speed=2.5):
        super().__init__(game, x, y, target_x, target_y, speed)
        self.image = game.assets.get_sprite('bullet_boss', 0)
        if self.image is None:
            self.image = pygame.Surface((6, 6))
            self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
