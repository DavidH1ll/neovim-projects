"""Room system"""
import pygame
import random
from settings import *


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, tile_image=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.image = tile_image
        if tile_image is None:
            self.image = pygame.Surface((w, h))
            self.image.fill(COLOR_WALL)
        self.is_door = False
    
    def draw(self, surf, cx, cy):
        if self.image:
            iw, ih = self.image.get_size()
            for dy in range(0, self.rect.height, ih):
                for dx in range(0, self.rect.width, iw):
                    surf.blit(self.image, (self.rect.x + cx + dx, self.rect.y + cy + dy))
        else:
            pygame.draw.rect(surf, COLOR_WALL, (self.rect.x + cx, self.rect.y + cy, self.rect.width, self.rect.height))


class Door(Wall):
    def __init__(self, x, y, w, h, direction):
        super().__init__(x, y, w, h)
        self.direction = direction
        self.is_closed = False
        self.is_door = True
        self.image = pygame.Surface((w, h))
        self.image.fill(COLOR_DOOR)
    
    def set_closed(self, closed):
        self.is_closed = closed
        self.image.fill(COLOR_DOOR if closed else COLOR_FLOOR)
    
    def draw(self, surf, cx, cy):
        if self.is_closed:
            super().draw(surf, cx, cy)


class LevelExit(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = game.assets.get_sprite('level_exit', 0)
        if self.image is None:
            self.image = pygame.Surface((16, 16))
            self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.active = False
    
    def update(self):
        pass
    
    def draw(self, surf, cx, cy):
        if self.active:
            surf.blit(self.image, (self.rect.x + cx, self.rect.y + cy))


class Room:
    def __init__(self, x, y, width, height, room_type=ROOM_NORMAL):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.room_type = room_type
        
        self.connections = [False, False, False, False]  # up, right, down, left
        self.wall_positions = []
        self.door_positions = []
        self.wall_sprites = []
        self.door_sprites = []
        self.enemies_spawned = False
        self.enemies_defeated = False
        self.close_when_entered = (room_type == ROOM_NORMAL)
        self.is_active = False
        
        self.floor_tiles = []
        self._generate_layout()
    
    def _generate_layout(self):
        self.wall_positions.clear()
        self.door_positions.clear()
        self.floor_tiles.clear()
        
        cols = self.width // TILE_SIZE
        rows = self.height // TILE_SIZE
        
        for row in range(rows):
            for col in range(cols):
                tx = self.x + col * TILE_SIZE
                ty = self.y + row * TILE_SIZE
                
                is_wall = (row == 0 or row == rows - 1 or col == 0 or col == cols - 1)
                is_door = False
                
                if is_wall:
                    if row == 0 and self.connections[DIR_UP] and col == cols // 2:
                        is_door = True
                    elif row == rows - 1 and self.connections[DIR_DOWN] and col == cols // 2:
                        is_door = True
                    elif col == 0 and self.connections[DIR_LEFT] and row == rows // 2:
                        is_door = True
                    elif col == cols - 1 and self.connections[DIR_RIGHT] and row == rows // 2:
                        is_door = True
                
                if is_door:
                    self.door_positions.append((tx, ty, TILE_SIZE, TILE_SIZE))
                elif is_wall:
                    self.wall_positions.append((tx, ty, TILE_SIZE, TILE_SIZE))
                else:
                    self.floor_tiles.append((tx, ty))
    
    @property
    def center_x(self):
        return self.x + self.width // 2
    
    @property
    def center_y(self):
        return self.y + self.height // 2
    
    def set_connections(self, up, right, down, left):
        self.connections = [up, right, down, left]
        self._generate_layout()
    
    def populate(self, game):
        # Create wall sprites
        for wx, wy, ww, wh in self.wall_positions:
            wall = Wall(wx, wy, ww, wh)
            self.wall_sprites.append(wall)
            game.add_wall(wall)
        
        # Create door sprites
        for dx, dy, dw, dh in self.door_positions:
            door = Door(dx, dy, dw, dh, DIR_UP)
            self.door_sprites.append(door)
            game.add_door(door)
        
        # Spawn enemies in normal rooms
        if self.room_type == ROOM_NORMAL and not self.enemies_spawned:
            count = random.randint(2, 5)
            for _ in range(count):
                ex = self.x + random.randint(48, self.width - 48)
                ey = self.y + random.randint(48, self.height - 48)
                etype = random.randint(0, 5)
                game.spawn_enemy(ex, ey, etype)
            self.enemies_spawned = True
        
        # Spawn breakables
        if self.room_type != ROOM_START:
            for _ in range(random.randint(1, 3)):
                bx = self.x + random.randint(48, self.width - 48)
                by = self.y + random.randint(48, self.height - 48)
                game.spawn_breakable(bx, by)
        
        # Boss room
        if self.room_type == ROOM_END:
            game.spawn_boss(self)
            exit_obj = LevelExit(game, self.center_x, self.center_y)
            exit_obj.active = False
            game.add_level_exit(exit_obj)
    
    def on_enter(self):
        self.is_active = True
        if self.close_when_entered and not self.enemies_defeated:
            for door in self.door_sprites:
                door.set_closed(True)
    
    def check_enemies_cleared(self, game):
        if self.close_when_entered and not self.enemies_defeated:
            alive = 0
            for enemy in game.enemies:
                if self.rect.collidepoint(enemy.rect.center):
                    alive += 1
            if alive == 0:
                self.enemies_defeated = True
                for door in self.door_sprites:
                    door.set_closed(False)
                
                if self.room_type == ROOM_END:
                    for exit_obj in game.level_exits:
                        exit_obj.active = True
    
    def draw(self, surf, cx, cy):
        for fx, fy in self.floor_tiles:
            pygame.draw.rect(surf, COLOR_FLOOR, (fx + cx, fy + cy, TILE_SIZE, TILE_SIZE))
        
        for wall in self.wall_sprites:
            wall.draw(surf, cx, cy)
        
        for door in self.door_sprites:
            door.draw(surf, cx, cy)
