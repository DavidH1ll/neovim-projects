"""Asset loading and sprite sheet management"""
import pygame
import os
from PIL import Image
from settings import SCALE, TILE_SIZE

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")


def pil_to_surface(pil_img):
    """Convert PIL Image to pygame Surface."""
    mode = pil_img.mode
    if mode == 'RGBA':
        raw_str = pil_img.tobytes('raw', 'RGBA')
        return pygame.image.fromstring(raw_str, pil_img.size, 'RGBA')
    elif mode == 'RGB':
        raw_str = pil_img.tobytes('raw', 'RGB')
        return pygame.image.fromstring(raw_str, pil_img.size, 'RGB')
    else:
        pil_img = pil_img.convert('RGBA')
        raw_str = pil_img.tobytes('raw', 'RGBA')
        return pygame.image.fromstring(raw_str, pil_img.size, 'RGBA')


def load_image(path, scale=1):
    """Load image at native resolution (scale=1 for pixel art)."""
    try:
        img = pygame.image.load(path).convert_alpha()
    except pygame.error:
        # Fallback to PIL if pygame lacks PNG support
        pil_img = Image.open(path).convert('RGBA')
        img = pil_to_surface(pil_img)
    if scale != 1:
        w, h = img.get_size()
        img = pygame.transform.scale(img, (w * scale, h * scale))
    return img


def slice_sheet(sheet, frame_width, frame_height, scale=1):
    """Slice a sprite sheet into a grid of frames."""
    frames = []
    sheet_w, sheet_h = sheet.get_size()
    fw = frame_width * scale
    fh = frame_height * scale
    cols = sheet_w // fw
    rows = sheet_h // fh

    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            frame = sheet.subsurface(rect).copy()
            frames.append(frame)
    return frames


def slice_sheet_custom(sheet, rects, scale=1):
    """Slice a sprite sheet using custom rects (native pixel coords)."""
    frames = []
    for r in rects:
        rect = pygame.Rect(r[0] * scale, r[1] * scale, r[2] * scale, r[3] * scale)
        if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
            frame = sheet.subsurface(rect).copy()
            frames.append(frame)
        else:
            frames.append(None)
    return frames


class Assets:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        self.images = {}
        self.sprites = {}
        
        # Load raw sheets
        self.sheets = {}
        for fname in os.listdir(ASSETS_DIR):
            if fname.lower().endswith('.png'):
                path = os.path.join(ASSETS_DIR, fname)
                key = fname.replace('.png', '').replace(' ', '_').lower()
                self.sheets[key] = load_image(path)
        
        # Character animations (4 directions x frames?)
        # Characters.png is 64x64 = 4x4 grid of 16x16
        chars = slice_sheet(self.sheets['characters'], 16, 16)
        self.sprites['player_idle'] = [chars[0]]
        self.sprites['player_move'] = [chars[0], chars[1], chars[2], chars[3]]
        self.sprites['player_dash'] = [chars[4]]
        self.sprites['char_2'] = chars[4:8]
        self.sprites['char_3'] = chars[8:12]
        self.sprites['shadow'] = [chars[-1]] if len(chars) >= 16 else []
        
        # Enemies
        enemies = slice_sheet(self.sheets['enemies'], 16, 16)
        self.sprites['enemy_blob'] = [enemies[0], enemies[1]]
        self.sprites['enemy_coward'] = [enemies[2], enemies[3]]
        self.sprites['enemy_dumb'] = [enemies[4], enemies[5]]
        self.sprites['enemy_fire'] = [enemies[6], enemies[7]]
        self.sprites['enemy_machine'] = [enemies[8], enemies[9]]
        self.sprites['enemy_skeleton'] = [enemies[10], enemies[11]]
        self.sprites['enemy_boss_eye'] = [enemies[12], enemies[13], enemies[14], enemies[15]]
        
        # Boss Eye (64x64 = 4x4 of 16x16)
        boss_eye = slice_sheet(self.sheets['bosseye'], 16, 16)
        self.sprites['boss_eye'] = boss_eye
        
        # Guns
        # Guns.png is 64x128 with irregular sprites. Use approximate grid.
        guns_sheet = self.sheets['guns']
        self.sprites['guns'] = []
        # Approximate positions in native pixels based on meta
        gun_rects = [
            (8, 116, 18, 11), (39, 115, 20, 13),
            (1, 99, 30, 11), (32, 98, 32, 13),
            (3, 81, 20, 11), (34, 80, 22, 13),
            (4, 62, 19, 13), (35, 61, 21, 15),
            (1, 46, 28, 10), (32, 45, 30, 12),
            (1, 26, 30, 14), (32, 25, 32, 16),
            (2, 2, 21, 20), (33, 1, 23, 22),
        ]
        self.sprites['guns'] = slice_sheet_custom(guns_sheet, gun_rects)
        
        # Bullets
        pb = slice_sheet(self.sheets['player_bullets'], 16, 16)
        self.sprites['bullet_player'] = pb[:4] if len(pb) >= 4 else pb
        
        eb = slice_sheet(self.sheets['enemy_bullets'], 8, 8)
        if not eb:
            eb = [self.sheets['enemy_bullets']]
        self.sprites['bullet_enemy'] = eb
        
        # Boss bullet
        self.sprites['bullet_boss'] = [self.sheets.get('bosseye', self.sheets['enemy_bullets'])]
        
        # Splatter
        splatter = slice_sheet(self.sheets['splatter'], 16, 16)
        self.sprites['splatter'] = splatter
        
        # Breakable
        breakable = slice_sheet(self.sheets['breakable'], 16, 16)
        self.sprites['breakable'] = breakable
        self.sprites['broken_piece'] = breakable[:6] if len(breakable) >= 6 else breakable
        
        # Level Objects
        obj = slice_sheet(self.sheets['level_objects'], 16, 16)
        self.sprites['level_exit'] = [obj[0]] if len(obj) > 0 else []
        self.sprites['chest'] = [obj[1]] if len(obj) > 1 else []
        self.sprites['cage'] = [obj[2]] if len(obj) > 2 else []
        
        # Pickups
        pickups = slice_sheet(self.sheets['pickups'], 16, 16)
        self.sprites['pickup_coin'] = [pickups[0]] if len(pickups) > 0 else []
        self.sprites['pickup_health'] = [pickups[1]] if len(pickups) > 1 else []
        self.sprites['pickup_gun'] = [pickups[2]] if len(pickups) > 2 else []
        
        # Map
        map_rooms = slice_sheet(self.sheets['map_rooms'], 16, 16)
        self.sprites['map_room'] = map_rooms
        
        # UI
        self.images['ui_health_outer'] = self.sheets.get('ui_healthbar_outer')
        self.images['ui_health_fill'] = self.sheets.get('ui_healthbar_fill')
        self.images['ui_gun_frame'] = self.sheets.get('hud_gun_frame')
        self.images['boss_health_bar'] = self.sheets.get('boss_health_name_bar')
        self.images['logo'] = self.sheets.get('logo')
        
        # Gun icons
        gun_icons = slice_sheet(self.sheets['hud_gun_icons'], 16, 16)
        self.sprites['gun_icons'] = gun_icons
        
        # Tilesets
        for i in [1, 2, 3]:
            key = f'dungeon_{i}'
            sheet = self.sheets.get(f'dungeon_{i}_tiles')
            if sheet:
                tiles = slice_sheet(sheet, 16, 16)
                self.sprites[key] = tiles
        
        # Crosshair
        self.images['crosshair'] = self.sheets.get('crosshair')
    
    def get_image(self, name):
        return self.images.get(name.lower())
    
    def get_sprite(self, name, index=0):
        sprites = self.sprites.get(name.lower(), [])
        if sprites and index < len(sprites) and sprites[index] is not None:
            return sprites[index]
        return None
    
    def get_sprites(self, name):
        return self.sprites.get(name.lower(), [])
    
    def get_tile(self, dungeon_num, index):
        key = f'dungeon_{dungeon_num}'
        tiles = self.sprites.get(key, [])
        if index < len(tiles):
            return tiles[index]
        return None
