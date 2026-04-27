"""Procedural level generation"""
import random
from settings import *
from room import Room


class LevelGenerator:
    def __init__(self, game):
        self.game = game
        self.distance_to_end = 5 + self.game.level_num * 2
        self.include_shop = True
        self.include_chest = True
        self.min_distance_to_shop = 1
        self.max_distance_to_shop = max(1, self.distance_to_end - 2)
    
    def generate(self):
        # Grid-based generation
        rooms = []
        positions = [(0, 0)]
        
        # Random walk
        x, y = 0, 0
        for i in range(self.distance_to_end):
            direction = random.randint(0, 3)
            if direction == DIR_UP:
                y -= 1
            elif direction == DIR_RIGHT:
                x += 1
            elif direction == DIR_DOWN:
                y += 1
            elif direction == DIR_LEFT:
                x -= 1
            
            # Avoid overlap
            attempts = 0
            while (x, y) in positions and attempts < 20:
                direction = random.randint(0, 3)
                if direction == DIR_UP:
                    y -= 1
                elif direction == DIR_RIGHT:
                    x += 1
                elif direction == DIR_DOWN:
                    y += 1
                elif direction == DIR_LEFT:
                    x -= 1
                attempts += 1
            
            if (x, y) not in positions:
                positions.append((x, y))
        
        # If we got fewer rooms than expected, fill in gaps
        if len(positions) < self.distance_to_end + 1:
            # Try to extend
            while len(positions) < self.distance_to_end + 1:
                last_x, last_y = positions[-1]
                direction = random.randint(0, 3)
                nx, ny = last_x, last_y
                if direction == DIR_UP:
                    ny -= 1
                elif direction == DIR_RIGHT:
                    nx += 1
                elif direction == DIR_DOWN:
                    ny += 1
                elif direction == DIR_LEFT:
                    nx -= 1
                if (nx, ny) not in positions:
                    positions.append((nx, ny))
        
        # Determine room types
        room_types = [ROOM_NORMAL] * len(positions)
        room_types[0] = ROOM_START
        room_types[-1] = ROOM_END
        
        if self.include_shop and len(positions) > 3:
            shop_idx = random.randint(self.min_distance_to_shop, min(self.max_distance_to_shop, len(positions) - 2))
            room_types[shop_idx] = ROOM_SHOP
        
        if self.include_chest and len(positions) > 4:
            chest_idx = random.randint(self.min_distance_to_shop, min(self.max_distance_to_shop, len(positions) - 2))
            if room_types[chest_idx] == ROOM_NORMAL:
                room_types[chest_idx] = ROOM_CHEST
            else:
                # Try next
                for i in range(chest_idx + 1, len(positions) - 1):
                    if room_types[i] == ROOM_NORMAL:
                        room_types[i] = ROOM_CHEST
                        break
        
        # Create rooms with proper pixel positions
        room_dict = {}
        for i, (gx, gy) in enumerate(positions):
            px = gx * ROOM_X_OFFSET
            py = gy * ROOM_Y_OFFSET
            room = Room(px, py, ROOM_WIDTH, ROOM_HEIGHT, room_types[i])
            rooms.append(room)
            room_dict[(gx, gy)] = room
        
        # Set connections
        for i, (gx, gy) in enumerate(positions):
            room = rooms[i]
            up = (gx, gy - 1) in room_dict
            right = (gx + 1, gy) in room_dict
            down = (gx, gy + 1) in room_dict
            left = (gx - 1, gy) in room_dict
            room.set_connections(up, right, down, left)
        
        return rooms
