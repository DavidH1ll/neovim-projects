"""Enemy controller"""
import pygame
import math
import random
from settings import *
from utils import dist, angle_between
from bullet import EnemyBullet


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, enemy_type):
        super().__init__()
        self.game = game
        self.enemy_type = enemy_type
        
        # Sprite mapping
        sprite_names = {
            ENEMY_BLOB: 'enemy_blob',
            ENEMY_COWARD: 'enemy_coward',
            ENEMY_DUMB_SHOOTER: 'enemy_dumb',
            ENEMY_FIRE: 'enemy_fire',
            ENEMY_MACHINE_GUN: 'enemy_machine',
            ENEMY_SKELETON: 'enemy_skeleton',
        }
        name = sprite_names.get(enemy_type, 'enemy_blob')
        sprites = game.assets.get_sprites(name)
        self.image = sprites[0] if sprites else pygame.Surface((16, 16))
        if self.image is None:
            self.image = pygame.Surface((16, 16))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(0, 0, 12, 12)
        self.hitbox.center = self.rect.center
        
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        
        # Config based on type
        configs = {
            ENEMY_BLOB: {'health': 100, 'speed': 0.8, 'chase': True, 'shoot': False, 'range': 80},
            ENEMY_COWARD: {'health': 80, 'speed': 1.2, 'chase': False, 'shoot': True, 'range': 100, 'runaway': True},
            ENEMY_DUMB_SHOOTER: {'health': 60, 'speed': 0.5, 'chase': False, 'shoot': True, 'range': 120, 'dumb': True},
            ENEMY_FIRE: {'health': 150, 'speed': 0.6, 'chase': True, 'shoot': False, 'range': 60},
            ENEMY_MACHINE_GUN: {'health': 120, 'speed': 0.7, 'chase': True, 'shoot': True, 'range': 140, 'firerate': 15},
            ENEMY_SKELETON: {'health': 80, 'speed': 1.0, 'chase': True, 'shoot': False, 'range': 80, 'wander': True},
        }
        cfg = configs.get(enemy_type, configs[ENEMY_BLOB])
        
        self.max_health = cfg['health']
        self.health = self.max_health
        self.move_speed = cfg['speed']
        self.should_chase = cfg.get('chase', False)
        self.should_shoot = cfg.get('shoot', False)
        self.should_runaway = cfg.get('runaway', False)
        self.should_wander = cfg.get('wander', False)
        self.chase_range = cfg.get('range', 80)
        self.shoot_range = cfg.get('range', 100)
        self.fire_rate = cfg.get('firerate', 45)
        self.dumb_shoot = cfg.get('dumb', False)
        self.runaway_range = 60
        
        self.fire_timer = 0
        self.move_shift_delay = 30
        self.wander_counter = 0
        self.pause_counter = random.randint(30, 60)
        self.wander_dir = (0, 0)
        
        self.anim_timer = 0
        self.anim_frame = 0
        self.facing_right = True
    
    def update(self):
        if not self.game.player or not self.game.player.alive():
            self.vx = 0
            self.vy = 0
            return
        
        player = self.game.player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        move_dir = (0, 0)
        
        # Run away behavior
        if self.should_runaway:
            if distance < self.runaway_range:
                move_dir = (-dx, -dy)
            else:
                self.move_shift_delay -= 1
                if self.move_shift_delay <= 0:
                    move_dir = (dx, dy)
                    self.move_shift_delay = 30
        
        # Chase behavior
        if distance < self.chase_range and self.should_chase:
            move_dir = (dx, dy)
        else:
            # Wander behavior
            if self.should_wander:
                if self.wander_counter > 0:
                    self.wander_counter -= 1
                    move_dir = self.wander_dir
                    if self.wander_counter <= 0:
                        self.pause_counter = random.randint(30, 60)
                elif self.pause_counter > 0:
                    self.pause_counter -= 1
                    if self.pause_counter <= 0:
                        self.wander_counter = random.randint(40, 80)
                        angle = random.uniform(0, math.pi * 2)
                        self.wander_dir = (math.cos(angle), math.sin(angle))
        
        # Normalize
        mx, my = move_dir
        mag = math.sqrt(mx*mx + my*my)
        if mag > 0:
            mx /= mag
            my /= mag
            self.facing_right = mx > 0
        
        self.vx = mx * self.move_speed
        self.vy = my * self.move_speed
        
        # Apply movement
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.hitbox.center = self.rect.center
        
        # Wall collision
        self._collide_with_walls()
        
        # Shoot
        if self.should_shoot and distance < self.shoot_range:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                if self.dumb_shoot:
                    self.fire_timer = random.randint(self.fire_rate // 2, self.fire_rate)
                else:
                    self.fire_timer = self.fire_rate
                self._shoot(player.rect.centerx, player.rect.centery)
        
        # Animation
        self._animate()
    
    def _collide_with_walls(self):
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
        
        for door in self.game.doors:
            if door.is_closed and self.hitbox.colliderect(door.rect):
                if self.vx > 0:
                    self.hitbox.right = door.rect.left
                elif self.vx < 0:
                    self.hitbox.left = door.rect.right
                if self.vy > 0:
                    self.hitbox.bottom = door.rect.top
                elif self.vy < 0:
                    self.hitbox.top = door.rect.bottom
                self.rect.center = self.hitbox.center
                self.x = float(self.rect.centerx)
                self.y = float(self.rect.centery)
    
    def _shoot(self, target_x, target_y):
        bullet = EnemyBullet(self.game, self.rect.centerx, self.rect.centery, target_x, target_y)
        self.game.enemy_bullets.add(bullet)
        self.game.all_sprites.add(bullet)
        self.game.audio.play_sfx('shoot4', 0.2)
    
    def _animate(self):
        self.anim_timer += 1
        sprite_names = {
            ENEMY_BLOB: 'enemy_blob',
            ENEMY_COWARD: 'enemy_coward',
            ENEMY_DUMB_SHOOTER: 'enemy_dumb',
            ENEMY_FIRE: 'enemy_fire',
            ENEMY_MACHINE_GUN: 'enemy_machine',
            ENEMY_SKELETON: 'enemy_skeleton',
        }
        name = sprite_names.get(self.enemy_type, 'enemy_blob')
        sprites = self.game.assets.get_sprites(name)
        
        if sprites and len(sprites) > 1:
            frame = (self.anim_timer // 10) % len(sprites)
            img = sprites[frame]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            self.image = img
    
    def take_damage(self, amount):
        self.health -= amount
        self.game.audio.play_sfx('enemy_hurt', 0.3)
        self.game.particles.spawn_hit(self.rect.centerx, self.rect.centery, (255, 100, 100), 5)
        
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.game.audio.play_sfx('enemy_death', 0.4)
        self.game.particles.spawn_explosion(self.rect.centerx, self.rect.centery, (255, 50, 50), 10)
        
        # Splatter
        splatter_imgs = self.game.assets.get_sprites('splatter')
        if splatter_imgs:
            self.game.particles.spawn_splatter(self.rect.centerx, self.rect.centery, splatter_imgs)
        
        # Drop item
        if random.random() < 0.3:
            drop_type = random.choice([PICKUP_COIN, PICKUP_COIN, PICKUP_HEALTH])
            self.game.spawn_pickup(self.rect.centerx, self.rect.centery, drop_type)
        
        self.kill()
        
        # Check if room cleared
        if self.game.current_room:
            self.game.current_room.check_enemies_cleared(self.game)
    
    def draw(self, surf, cx, cy):
        shadow = self.game.assets.get_sprite('shadow', 0)
        if shadow:
            sx = self.rect.centerx - shadow.get_width() // 2 + cx
            sy = self.rect.bottom - shadow.get_height() // 2 + cy
            surf.blit(shadow, (sx, sy))
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))
