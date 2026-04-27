"""Player controller"""
import pygame
import math
from settings import *
from utils import angle_between, vec_from_angle
from bullet import PlayerBullet


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.assets = game.assets
        
        self.image = self.assets.get_sprite('player_idle', 0)
        if self.image is None:
            self.image = pygame.Surface((16, 16))
            self.image.fill((0, 200, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(0, 0, 10, 10)
        self.hitbox.center = self.rect.center
        
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        
        self.move_speed = 1.5
        self.dash_speed = 4.0
        self.dash_length = 10
        self.dash_cooldown = 60
        self.dash_invincibility = 30
        self.dash_counter = 0
        self.dash_cool_counter = 0
        
        self.can_move = True
        self.facing_right = True
        
        self.max_health = 6
        self.health = 6
        self.invincible_timer = 0
        
        self.guns = ['pistol', 'shotgun', 'machine_gun']
        self.current_gun_idx = 0
        self.shot_timer = 0
        
        self.anim_timer = 0
        self.anim_frame = 0
        self.is_moving = False
        self.is_dashing = False
    
    @property
    def current_gun(self):
        return self.guns[self.current_gun_idx]
    
    def update(self):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if self.can_move and not self.game.is_paused:
            # Movement
            dx = 0
            dy = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1
            
            # Normalize diagonal
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            
            speed = self.dash_speed if self.dash_counter > 0 else self.move_speed
            self.vx = dx * speed
            self.vy = dy * speed
            
            self.is_moving = (dx != 0 or dy != 0)
            
            # Facing direction based on mouse
            mx, my = pygame.mouse.get_pos()
            mx = mx // SCALE
            my = my // SCALE
            cx, cy = self.game.camera.get_offset()
            screen_x = self.rect.centerx + cx
            screen_y = self.rect.centery + cy
            
            if mx < screen_x:
                self.facing_right = False
            else:
                self.facing_right = True
            
            # Dash timer
            if self.dash_counter > 0:
                self.dash_counter -= 1
                if self.dash_counter <= 0:
                    self.dash_cool_counter = self.dash_cooldown
                    self.is_dashing = False
            
            if self.dash_cool_counter > 0:
                self.dash_cool_counter -= 1
            
            # Shooting
            if mouse_pressed[0] and self.shot_timer <= 0:
                self.shoot(mx - screen_x, my - screen_y)
            
            if self.shot_timer > 0:
                self.shot_timer -= 1
        else:
            self.vx = 0
            self.vy = 0
            self.is_moving = False
        
        # Invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Apply velocity
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.hitbox.center = self.rect.center
        
        # Wall collisions
        self._collide_with_walls()
        
        # Animation
        self._animate()
    
    def _collide_with_walls(self):
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                # Simple resolution: push back
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
    
    def _animate(self):
        self.anim_timer += 1
        
        if self.dash_counter > 0:
            anim = self.assets.get_sprites('player_dash')
        elif self.is_moving:
            anim = self.assets.get_sprites('player_move')
        else:
            anim = self.assets.get_sprites('player_idle')
        
        if anim:
            frame_duration = 8
            self.anim_frame = (self.anim_timer // frame_duration) % len(anim)
            img = anim[self.anim_frame]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            
            # Flash when invincible
            if self.invincible_timer > 0 and self.anim_timer % 4 < 2:
                img = img.copy()
                img.set_alpha(128)
            
            self.image = img
    
    def shoot(self, dx, dy):
        angle = math.atan2(dy, dx)
        
        if self.current_gun == 'pistol':
            self._fire_bullet(angle, 4)
            self.shot_timer = 20
            self.game.audio.play_sfx('shoot1', 0.3)
        elif self.current_gun == 'shotgun':
            for offset in [-0.3, -0.15, 0, 0.15, 0.3]:
                self._fire_bullet(angle + offset, 3.5)
            self.shot_timer = 45
            self.game.audio.play_sfx('shoot3', 0.3)
        elif self.current_gun == 'machine_gun':
            spread = random.uniform(-0.1, 0.1)
            self._fire_bullet(angle + spread, 4.5)
            self.shot_timer = 6
            self.game.audio.play_sfx('shoot2', 0.2)
    
    def _fire_bullet(self, angle, speed):
        bx = self.rect.centerx + math.cos(angle) * 12
        by = self.rect.centery + math.sin(angle) * 12
        bullet = PlayerBullet(self.game, bx, by, angle, speed)
        self.game.bullets.add(bullet)
        self.game.all_sprites.add(bullet)
    
    def dash(self):
        if self.dash_cool_counter <= 0 and self.dash_counter <= 0:
            self.dash_counter = self.dash_length
            self.is_dashing = True
            self.invincible_timer = self.dash_invincibility
            self.game.audio.play_sfx('player_dash', 0.4)
            self.game.particles.spawn_hit(self.rect.centerx, self.rect.centery, (200, 200, 255), 8)
    
    def switch_gun(self):
        self.current_gun_idx = (self.current_gun_idx + 1) % len(self.guns)
        self.game.audio.play_sfx('pickup_gun', 0.3)
    
    def take_damage(self, amount=1):
        if self.invincible_timer > 0:
            return
        
        self.health -= amount
        self.invincible_timer = 60
        self.game.audio.play_sfx('player_hurt', 0.5)
        self.game.screen_shake(3, 10)
        
        if self.health <= 0:
            self.game.audio.play_sfx('player_death', 0.6)
            self.game.audio.play_music('game_over', loops=0)
            self.game.state = STATE_GAMEOVER
            self.kill()
    
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        self.game.audio.play_sfx('pickup_health', 0.4)
    
    def draw(self, surf, cx, cy):
        # Draw shadow
        shadow = self.assets.get_sprite('shadow', 0)
        if shadow:
            sx = self.rect.centerx - shadow.get_width() // 2 + cx
            sy = self.rect.bottom - shadow.get_height() // 2 + cy
            surf.blit(shadow, (sx, sy))
        
        surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))
        
        # Draw gun arm
        gun_img = self.assets.get_sprite('guns', self.current_gun_idx)
        if gun_img:
            mx, my = pygame.mouse.get_pos()
            mx = mx // SCALE
            my = my // SCALE
            cx_off, cy_off = self.game.camera.get_offset()
            screen_x = self.rect.centerx + cx_off
            screen_y = self.rect.centery + cy_off
            angle = math.atan2(my - screen_y, mx - screen_x)
            
            rot_gun = pygame.transform.rotate(gun_img, -math.degrees(angle))
            if not self.facing_right:
                rot_gun = pygame.transform.flip(rot_gun, False, True)
            
            gx = self.rect.centerx - rot_gun.get_width() // 2 + cx
            gy = self.rect.centery - rot_gun.get_height() // 2 + cy
            surf.blit(rot_gun, (gx, gy))
