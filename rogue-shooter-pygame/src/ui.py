"""UI system"""
import pygame
from settings import *
from utils import render_text


class UI:
    def __init__(self, game):
        self.game = game
        self.show_minimap = True
        self.show_big_map = False
        self.boss_health_visible = False
    
    def update(self):
        # Boss health visibility
        if self.game.boss and self.game.boss.alive():
            self.boss_health_visible = True
        else:
            self.boss_health_visible = False
    
    def toggle_minimap(self):
        self.show_minimap = not self.show_minimap
    
    def toggle_big_map(self):
        self.show_big_map = not self.show_big_map
        if self.show_big_map:
            self.show_minimap = False
    
    def draw(self, surf):
        player = self.game.player
        if not player or not player.alive():
            return
        
        # Health bar
        self._draw_health_bar(surf, player)
        
        # Gun display
        self._draw_gun_display(surf, player)
        
        # Coins
        self._draw_coins(surf)
        
        # Boss health
        if self.boss_health_visible:
            self._draw_boss_health(surf)
        
        # Minimap
        if self.show_minimap and not self.show_big_map:
            self._draw_minimap(surf)
        
        # Big map
        if self.show_big_map:
            self._draw_big_map(surf)
        
        # Crosshair
        self._draw_crosshair(surf)
    
    def _draw_health_bar(self, surf, player):
        x = 4
        y = 4
        w = 60
        h = 8
        
        # Background
        pygame.draw.rect(surf, (50, 50, 50), (x, y, w, h))
        
        # Fill
        ratio = player.health / player.max_health
        fill_w = int(w * ratio)
        color = (200, 50, 50) if ratio < 0.3 else (50, 200, 50)
        pygame.draw.rect(surf, color, (x, y, fill_w, h))
        
        # Border
        pygame.draw.rect(surf, (255, 255, 255), (x, y, w, h), 1)
        
        # Text
        render_text(surf, f"{player.health}/{player.max_health}", 12, (x + 2, y + 1))
    
    def _draw_gun_display(self, surf, player):
        x = NATIVE_W - 40
        y = 4
        
        # Frame
        frame = self.game.assets.get_image('ui_gun_frame')
        if frame:
            surf.blit(frame, (x, y))
        
        # Gun icon
        icons = self.game.assets.get_sprites('gun_icons')
        if icons and player.current_gun_idx < len(icons):
            icon = icons[player.current_gun_idx]
            if icon:
                surf.blit(icon, (x + 4, y + 4))
        
        # Gun name
        name = player.current_gun.replace('_', ' ').title()
        render_text(surf, name, 10, (x, y + 20))
    
    def _draw_coins(self, surf):
        x = NATIVE_W - 50
        y = NATIVE_H - 14
        render_text(surf, f"${self.game.current_coins}", 12, (x, y), color=(255, 215, 0))
    
    def _draw_boss_health(self, surf):
        if not self.game.boss:
            return
        
        bar_w = 100
        bar_h = 6
        x = (NATIVE_W - bar_w) // 2
        y = 4
        
        ratio = self.game.boss.health / self.game.boss.max_health
        fill_w = int(bar_w * ratio)
        
        pygame.draw.rect(surf, (80, 20, 20), (x, y, bar_w, bar_h))
        pygame.draw.rect(surf, (255, 50, 50), (x, y, fill_w, bar_h))
        pygame.draw.rect(surf, (255, 255, 255), (x, y, bar_w, bar_h), 1)
    
    def _draw_minimap(self, surf):
        size = 4
        ox = NATIVE_W - 40
        oy = 30
        
        for room in self.game.rooms:
            mx = ox + (room.x // ROOM_X_OFFSET) * size
            my = oy + (room.y // ROOM_Y_OFFSET) * size
            
            colors = {
                ROOM_START: (0, 255, 0),
                ROOM_NORMAL: (150, 150, 150),
                ROOM_END: (255, 0, 0),
                ROOM_SHOP: (255, 215, 0),
                ROOM_CHEST: (0, 150, 255),
            }
            color = colors.get(room.room_type, (150, 150, 150))
            
            if room == self.game.current_room:
                color = (255, 255, 255)
            
            pygame.draw.rect(surf, color, (mx, my, size, size))
            pygame.draw.rect(surf, (50, 50, 50), (mx, my, size, size), 1)
    
    def _draw_big_map(self, surf):
        overlay = pygame.Surface((NATIVE_W, NATIVE_H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surf.blit(overlay, (0, 0))
        
        size = 8
        cx = NATIVE_W // 2
        cy = NATIVE_H // 2
        
        for room in self.game.rooms:
            mx = cx + (room.x // ROOM_X_OFFSET) * size
            my = cy + (room.y // ROOM_Y_OFFSET) * size
            
            colors = {
                ROOM_START: (0, 255, 0),
                ROOM_NORMAL: (150, 150, 150),
                ROOM_END: (255, 0, 0),
                ROOM_SHOP: (255, 215, 0),
                ROOM_CHEST: (0, 150, 255),
            }
            color = colors.get(room.room_type, (150, 150, 150))
            
            if room == self.game.current_room:
                color = (255, 255, 255)
            
            pygame.draw.rect(surf, color, (mx, my, size, size))
            pygame.draw.rect(surf, (50, 50, 50), (mx, my, size, size), 1)
        
        render_text(surf, "Press M to close", 12, (4, NATIVE_H - 14), color=(200, 200, 200))
    
    def _draw_crosshair(self, surf):
        mx, my = pygame.mouse.get_pos()
        mx = mx // SCALE
        my = my // SCALE
        
        crosshair = self.game.assets.get_image('crosshair')
        if crosshair:
            rect = crosshair.get_rect(center=(mx, my))
            surf.blit(crosshair, rect)
        else:
            pygame.draw.circle(surf, (255, 255, 255), (mx, my), 3, 1)
