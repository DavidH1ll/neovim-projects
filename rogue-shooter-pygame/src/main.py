"""
Roguelike Shooter - Pygame Port
Main entry point
"""
import pygame
import sys
import random
import math

from settings import *
from assets import Assets
from audio_manager import AudioManager
from camera import Camera
from level_generator import LevelGenerator
from room import Room
from player import Player
from enemy import Enemy
from boss import Boss
from bullet import PlayerBullet, EnemyBullet, BossBullet
from pickup import Pickup
from breakable import Breakable
from particles import ParticleSystem
from ui import UI
from utils import render_text


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Roguelike Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.assets = Assets()
        self.audio = AudioManager()
        self.particles = ParticleSystem()
        self.camera = Camera()
        self.ui = UI(self)
        
        self.state = STATE_MENU
        self.level_num = 1
        self.current_coins = 0
        
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.breakables = pygame.sprite.Group()
        self.level_exits = pygame.sprite.Group()
        
        self.player = None
        self.rooms = []
        self.current_room = None
        self.boss = None
        
        self.is_paused = False
        self.shake_timer = 0
        self.shake_amount = 0
        
        self.fade_alpha = 255
        self.fade_target = 0
        self.fade_speed = 5
        
    def new_game(self):
        self.state = STATE_PLAY
        self.level_num = 1
        self.current_coins = 0
        self.start_level()
        
    def start_level(self):
        self.all_sprites.empty()
        self.walls.empty()
        self.doors.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.pickups.empty()
        self.breakables.empty()
        self.level_exits.empty()
        self.particles.clear()
        
        # Generate level
        gen = LevelGenerator(self)
        self.rooms = gen.generate()
        
        # Find start room
        start_room = self.rooms[0]
        for room in self.rooms:
            if room.room_type == ROOM_START:
                start_room = room
                break
        
        # Create player
        self.player = Player(self, start_room.center_x, start_room.center_y)
        self.all_sprites.add(self.player)
        
        # Set camera
        self.camera.snap_to_room(start_room)
        self.current_room = start_room
        
        # Populate rooms
        for room in self.rooms:
            room.populate(self)
        
        # Play level music
        self.audio.play_music(f"Level {self.level_num}")
        
        self.fade_alpha = 255
        self.fade_target = 0
        
    def spawn_enemy(self, x, y, enemy_type):
        enemy = Enemy(self, x, y, enemy_type)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        return enemy
    
    def spawn_boss(self, room):
        self.boss = Boss(self, room.center_x, room.center_y)
        self.all_sprites.add(self.boss)
        return self.boss
    
    def spawn_pickup(self, x, y, pickup_type):
        pickup = Pickup(self, x, y, pickup_type)
        self.pickups.add(pickup)
        self.all_sprites.add(pickup)
        return pickup
    
    def spawn_breakable(self, x, y):
        breakable = Breakable(self, x, y)
        self.breakables.add(breakable)
        self.all_sprites.add(breakable)
        return breakable
    
    def add_wall(self, wall):
        self.walls.add(wall)
    
    def add_door(self, door):
        self.doors.add(door)
    
    def add_level_exit(self, exit_obj):
        self.level_exits.add(exit_obj)
        self.all_sprites.add(exit_obj)
    
    def screen_shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_timer = duration
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAY:
                        self.toggle_pause()
                    elif self.state == STATE_PAUSE:
                        self.toggle_pause()
                
                if self.state == STATE_PLAY and not self.is_paused:
                    if event.key == pygame.K_q:
                        self.player.switch_gun()
                    if event.key == pygame.K_SPACE:
                        self.player.dash()
                    if event.key == pygame.K_m:
                        self.ui.toggle_big_map()
                    if event.key == pygame.K_TAB:
                        self.ui.toggle_minimap()
                
                if self.state == STATE_MENU:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.new_game()
                
                if self.state == STATE_GAMEOVER or self.state == STATE_VICTORY:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = STATE_MENU
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == STATE_MENU:
                    self.new_game()
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.state = STATE_PAUSE
        else:
            self.state = STATE_PLAY
    
    def update(self):
        if self.state != STATE_PLAY or self.is_paused:
            return
        
        dt = 1 / FPS
        
        # Update all sprites
        self.all_sprites.update()
        self.particles.update()
        self.ui.update()
        
        # Check room transitions
        if self.player and self.current_room:
            for room in self.rooms:
                if room.rect.collidepoint(self.player.rect.center):
                    if room != self.current_room:
                        self.current_room = room
                        self.camera.move_to_room(room)
                        room.on_enter()
                    break
        
        # Screen shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
        
        # Fade
        if self.fade_alpha > self.fade_target:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha < self.fade_target:
                self.fade_alpha = self.fade_target
        elif self.fade_alpha < self.fade_target:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha > self.fade_target:
                self.fade_alpha = self.fade_target
        
        # Check level complete (boss defeated + exit touched)
        if self.player and self.level_exits:
            hits = pygame.sprite.spritecollide(self.player, self.level_exits, False)
            if hits:
                self.level_num += 1
                if self.level_num > 3:
                    self.state = STATE_VICTORY
                    self.audio.play_music("VictoryMusic")
                else:
                    self.start_level()
    
    def draw(self):
        # Render to native surface
        native = pygame.Surface((NATIVE_W, NATIVE_H))
        
        if self.state == STATE_MENU:
            self.draw_menu(native)
        elif self.state == STATE_PLAY or self.state == STATE_PAUSE:
            self.draw_game(native)
        elif self.state == STATE_GAMEOVER:
            self.draw_game(native)
            self.draw_gameover(native)
        elif self.state == STATE_VICTORY:
            self.draw_game(native)
            self.draw_victory(native)
        
        # Scale to screen
        scaled = pygame.transform.scale(native, (WINDOW_W, WINDOW_H))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
    
    def draw_menu(self, surf):
        surf.fill(COLOR_BG)
        logo = self.assets.get_image("Logo")
        if logo:
            rect = logo.get_rect(center=(NATIVE_W//2, NATIVE_H//2 - 20))
            surf.blit(logo, rect)
        
        render_text(surf, "Press ENTER or Click to Start", 16, (NATIVE_W//2, NATIVE_H//2 + 30), center=True)
    
    def draw_game(self, surf):
        # Camera offset
        cx, cy = self.camera.get_offset()
        shake_x = random.randint(-self.shake_amount, self.shake_amount) if self.shake_timer > 0 else 0
        shake_y = random.randint(-self.shake_amount, self.shake_amount) if self.shake_timer > 0 else 0
        cx += shake_x
        cy += shake_y
        
        # Draw room backgrounds (only visible rooms)
        for room in self.rooms:
            if self.camera.can_see(room.rect):
                room.draw(surf, cx, cy)
        
        # Sort sprites by Y for depth
        sprites = sorted(self.all_sprites, key=lambda s: getattr(s, 'rect', pygame.Rect(0,0,1,1)).bottom)
        
        for sprite in sprites:
            if hasattr(sprite, 'draw'):
                sprite.draw(surf, cx, cy)
            elif hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                surf.blit(sprite.image, (sprite.rect.x + cx, sprite.rect.y + cy))
        
        # Draw particles
        self.particles.draw(surf, cx, cy)
        
        # Draw UI
        self.ui.draw(surf)
        
        # Fade overlay
        if self.fade_alpha > 0:
            fade = pygame.Surface((NATIVE_W, NATIVE_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(self.fade_alpha)
            surf.blit(fade, (0, 0))
        
        # Pause overlay
        if self.is_paused:
            overlay = pygame.Surface((NATIVE_W, NATIVE_H))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(150)
            surf.blit(overlay, (0, 0))
            render_text(surf, "PAUSED", 24, (NATIVE_W//2, NATIVE_H//2), center=True)
    
    def draw_gameover(self, surf):
        overlay = pygame.Surface((NATIVE_W, NATIVE_H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surf.blit(overlay, (0, 0))
        render_text(surf, "GAME OVER", 24, (NATIVE_W//2, NATIVE_H//2 - 10), color=(255, 0, 0), center=True)
        render_text(surf, "Press ENTER for Menu", 16, (NATIVE_W//2, NATIVE_H//2 + 10), center=True)
    
    def draw_victory(self, surf):
        overlay = pygame.Surface((NATIVE_W, NATIVE_H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surf.blit(overlay, (0, 0))
        render_text(surf, "VICTORY!", 24, (NATIVE_W//2, NATIVE_H//2 - 10), color=(255, 215, 0), center=True)
        render_text(surf, "Press ENTER for Menu", 16, (NATIVE_W//2, NATIVE_H//2 + 10), center=True)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
