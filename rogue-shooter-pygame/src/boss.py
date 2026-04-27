"""Boss controller"""
import pygame
import math
import random
from settings import *
from bullet import BossBullet


class Boss(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        sprites = game.assets.get_sprites('boss_eye')
        self.image = sprites[0] if sprites else pygame.Surface((32, 32))
        if self.image is None:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(0, 0, 24, 24)
        self.hitbox.center = self.rect.center
        
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        
        self.max_health = 500
        self.health = self.max_health
        self.move_speed = 0.8
        
        # Boss action sequences
        self.current_sequence = 0
        self.current_action = 0
        self.action_timer = 0
        self.shot_timer = 0
        
        self.sequences = [
            # Phase 1
            {
                'health_threshold': 300,
                'actions': [
                    {'duration': 120, 'move': True, 'chase': True, 'shoot': True, 'shot_interval': 30, 'shots': 4},
                    {'duration': 90, 'move': False, 'chase': False, 'shoot': True, 'shot_interval': 15, 'shots': 8},
                ]
            },
            # Phase 2
            {
                'health_threshold': 150,
                'actions': [
                    {'duration': 100, 'move': True, 'chase': True, 'shoot': True, 'shot_interval': 20, 'shots': 6},
                    {'duration': 80, 'move': True, 'chase': False, 'shoot': True, 'shot_interval': 10, 'shots': 12},
                ]
            },
            # Phase 3
            {
                'health_threshold': 0,
                'actions': [
                    {'duration': 90, 'move': True, 'chase': True, 'shoot': True, 'shot_interval': 15, 'shots': 8},
                    {'duration': 60, 'move': False, 'chase': False, 'shoot': True, 'shot_interval': 8, 'shots': 16},
                ]
            },
        ]
        
        self._set_action()
        
        self.anim_timer = 0
        self.facing_right = True
    
    def _set_action(self):
        seq = self.sequences[self.current_sequence]
        action = seq['actions'][self.current_action]
        self.action_timer = action['duration']
        self.shot_timer = action['shot_interval']
    
    def update(self):
        if not self.game.player or not self.game.player.alive():
            return
        
        player = self.game.player
        
        # Action timer
        self.action_timer -= 1
        if self.action_timer <= 0:
            self.current_action += 1
            seq = self.sequences[self.current_sequence]
            if self.current_action >= len(seq['actions']):
                self.current_action = 0
            self._set_action()
        
        seq = self.sequences[self.current_sequence]
        action = seq['actions'][self.current_action]
        
        # Movement
        move_dir = (0, 0)
        if action['move']:
            if action['chase']:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    move_dir = (dx/dist, dy/dist)
                    self.facing_right = dx > 0
        
        self.vx = move_dir[0] * self.move_speed
        self.vy = move_dir[1] * self.move_speed
        
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.hitbox.center = self.rect.center
        
        # Wall collision
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                if self.vx > 0:
                    self.hitbox.right = wall.rect.left
                elif self.vx < 0:
                    self.hitbox.left = wall.rect.right
                if self.vy > 0:
                    self.hitbox.bottom = wall.rect.top
                elif self.vy < 0:
                    self.hitbox.top = wall.rect.bottom
                self.rect.center = self.hitbox.center
                self.x = float(self.rect.centerx)
                self.y = float(self.rect.centery)
        
        # Shooting
        if action['shoot']:
            self.shot_timer -= 1
            if self.shot_timer <= 0:
                self.shot_timer = action['shot_interval']
                self._shoot_pattern(action['shots'])
        
        # Animation
        self.anim_timer += 1
        sprites = self.game.assets.get_sprites('boss_eye')
        if sprites:
            frame = (self.anim_timer // 8) % len(sprites)
            img = sprites[frame]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            self.image = img
    
    def _shoot_pattern(self, num_shots):
        player = self.game.player
        base_angle = math.atan2(player.rect.centery - self.rect.centery,
                                player.rect.centerx - self.rect.centerx)
        
        if num_shots <= 4:
            # Aimed shots
            for i in range(num_shots):
                offset = (i - num_shots/2) * 0.2
                bullet = BossBullet(self.game, self.rect.centerx, self.rect.centery,
                                    self.rect.centerx + math.cos(base_angle + offset),
                                    self.rect.centery + math.sin(base_angle + offset))
                self.game.enemy_bullets.add(bullet)
                self.game.all_sprites.add(bullet)
        else:
            # Spiral / circle pattern
            for i in range(num_shots):
                angle = base_angle + (i / num_shots) * math.pi * 2
                tx = self.rect.centerx + math.cos(angle)
                ty = self.rect.centery + math.sin(angle)
                bullet = BossBullet(self.game, self.rect.centerx, self.rect.centery, tx, ty)
                self.game.enemy_bullets.add(bullet)
                self.game.all_sprites.add(bullet)
        
        self.game.audio.play_sfx('shoot5', 0.3)
    
    def take_damage(self, amount):
        self.health -= amount
        self.game.screen_shake(2, 5)
        
        # Check phase transition
        seq = self.sequences[self.current_sequence]
        if self.health <= seq['health_threshold'] and self.current_sequence < len(self.sequences) - 1:
            self.current_sequence += 1
            self.current_action = 0
            self._set_action()
            self.game.particles.spawn_explosion(self.rect.centerx, self.rect.centery, (255, 100, 255), 20)
            self.game.audio.play_sfx('explosion', 0.5)
        
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.game.audio.play_sfx('explosion', 0.6)
        self.game.particles.spawn_explosion(self.rect.centerx, self.rect.centery, (255, 0, 255), 30)
        self.game.screen_shake(5, 30)
        
        # Activate exit
        for exit_obj in self.game.level_exits:
            exit_obj.active = True
            # Move away from player if too close
            if self.game.player:
                dx = exit_obj.rect.centerx - self.game.player.rect.centerx
                dy = exit_obj.rect.centery - self.game.player.rect.centery
                if math.sqrt(dx*dx + dy*dy) < 40:
                    exit_obj.rect.x += 40
        
        self.kill()
        self.game.boss = None
    
    def draw(self, surf, cx, cy):
        shadow = self.game.assets.get_sprite('shadow', 0)
        if shadow:
            sx = self.rect.centerx - shadow.get_width() // 2 + cx
            sy = self.rect.bottom - shadow.get_height() // 2 + cy
            surf.blit(shadow, (sx, sy))
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))
