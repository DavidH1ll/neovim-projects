#!/usr/bin/env python3
"""
Flappy Bird Clone — Enhanced Edition

A pygame-based clone of the classic Flappy Bird game.
Built while learning Neovim.

Enhancements:
- 2x screen size (576x1024) with crisp pixel art scaling
- Night mode toggle
- Bird color selector (Yellow / Red / Blue)
- Pause functionality
- Difficulty levels (Easy / Normal / Hard)
- Persistent leaderboard (saves to file)
- Day/night cycle that changes every 10 points

Assets: https://github.com/samuelcust/flappy-bird-assets
"""

import json
import math
import os
import random
import sys

import pygame
from PIL import Image

# ─── Configuration ───────────────────────────────────────────────────────────

# Original game resolution (kept for authentic pixel art)
GAME_WIDTH = 288
GAME_HEIGHT = 512

# Display resolution (2x scaled)
SCREEN_WIDTH = GAME_WIDTH * 2
SCREEN_HEIGHT = GAME_HEIGHT * 2
SCALE = 2

FPS = 60

# Physics (adjusted for the scaled feel)
GRAVITY = 0.25
FLAP_STRENGTH = -4.5
PIPE_GAP_DEFAULT = 100
PIPE_SPAWN_INTERVAL = 1200
GROUND_HEIGHT = 112
SCROLL_SPEED_DEFAULT = 2

# Difficulty presets
DIFFICULTIES = {
    "EASY":   {"gap": 120, "speed": 1.5, "spawn": 1500, "label": "Easy"},
    "NORMAL": {"gap": 100, "speed": 2.0, "spawn": 1200, "label": "Normal"},
    "HARD":   {"gap": 80,  "speed": 2.8, "spawn": 900,  "label": "Hard"},
}

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

# Bird colors
BIRD_COLORS = ["yellow", "red", "blue"]

# ─── Pygame Init ─────────────────────────────────────────────────────────────

pygame.init()

AUDIO_AVAILABLE = False
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except (pygame.error, NotImplementedError):
    print("Warning: Audio not available. Game will run without sound.")

FONT_AVAILABLE = False
try:
    pygame.font.init()
    FONT_AVAILABLE = True
except (pygame.error, NotImplementedError):
    print("Warning: Font rendering not available. Using fallback.")

# ─── Helpers ─────────────────────────────────────────────────────────────────


def load_sprite(name):
    """Load a sprite image from the assets directory."""
    path = os.path.join(SPRITES_DIR, name)
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error:
        img = Image.open(path).convert("RGBA")
        return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")


def load_sound(name):
    """Load a sound effect from the assets directory."""
    if not AUDIO_AVAILABLE:
        return None
    path = os.path.join(AUDIO_DIR, name)
    return pygame.mixer.Sound(path)


def load_number_sprites():
    """Load number sprites 0-9 for score display."""
    numbers = {}
    for i in range(10):
        numbers[i] = load_sprite(f"{i}.png")
    return numbers


def render_text(text, size, color, bold=True):
    """Render text to a pygame surface, with Pillow fallback."""
    if FONT_AVAILABLE:
        font = pygame.font.SysFont("Arial", size, bold=bold)
        return font.render(text, True, color)
    else:
        from PIL import ImageDraw, ImageFont
        try:
            pil_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except Exception:
            pil_font = ImageFont.load_default()
        bbox = pil_font.getbbox(text)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, -bbox[1]), text, font=pil_font, fill=color)
        return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")


# ─── Leaderboard ─────────────────────────────────────────────────────────────


def load_leaderboard():
    """Load leaderboard from JSON file."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_leaderboard(entries):
    """Save leaderboard to JSON file."""
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except IOError:
        pass


def add_score(entries, score, difficulty, color):
    """Add a new score entry and keep top 10."""
    entries.append({
        "score": score,
        "difficulty": difficulty,
        "bird_color": color,
    })
    entries.sort(key=lambda x: x["score"], reverse=True)
    return entries[:10]


# ─── Classes ─────────────────────────────────────────────────────────────────


class Bird:
    """The player-controlled bird."""

    def __init__(self, x, y, color="yellow"):
        self.x = x
        self.y = y
        self.velocity = 0
        self.rotation = 0
        self.color = color
        self.load_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 5

    def load_frames(self):
        """Load bird animation frames for the current color."""
        self.frames = [
            load_sprite(f"{self.color}bird-downflap.png"),
            load_sprite(f"{self.color}bird-midflap.png"),
            load_sprite(f"{self.color}bird-upflap.png"),
        ]

    def set_color(self, color):
        """Change the bird color."""
        self.color = color
        self.load_frames()

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        if self.velocity < 0:
            self.rotation = max(self.rotation - 3, -25)
        else:
            self.rotation = min(self.rotation + 3, 90)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.rotation = -25

    def draw(self, screen):
        frame = self.frames[self.frame_index]
        rotated = pygame.transform.rotate(frame, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

    def get_mask(self):
        return pygame.mask.from_surface(self.frames[self.frame_index])

    def get_rect(self):
        return self.frames[self.frame_index].get_rect(center=(self.x, self.y))


class Pipe:
    """A pair of pipes that the bird must fly through."""

    def __init__(self, x, gap_y, gap_size, pipe_color="green"):
        self.x = x
        self.gap_y = gap_y
        self.passed = False
        self.gap_size = gap_size

        self.pipe_img = load_sprite(f"pipe-{pipe_color}.png")
        self.pipe_width = self.pipe_img.get_width()
        self.pipe_height = self.pipe_img.get_height()

        self.top_pipe = pygame.transform.flip(self.pipe_img, False, True)
        self.top_y = gap_y - gap_size // 2 - self.pipe_height
        self.bottom_y = gap_y + gap_size // 2

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        screen.blit(self.top_pipe, (self.x, self.top_y))
        screen.blit(self.pipe_img, (self.x, self.bottom_y))

    def is_off_screen(self):
        return self.x < -self.pipe_width

    def get_top_mask(self):
        return pygame.mask.from_surface(self.top_pipe), (self.x, self.top_y)

    def get_bottom_mask(self):
        return pygame.mask.from_surface(self.pipe_img), (self.x, self.bottom_y)

    def collides_with(self, bird):
        bird_mask = bird.get_mask()
        bird_rect = bird.get_rect()

        top_mask, top_pos = self.get_top_mask()
        top_offset = (top_pos[0] - bird_rect.left, top_pos[1] - bird_rect.top)
        if bird_mask.overlap(top_mask, top_offset):
            return True

        bottom_mask, bottom_pos = self.get_bottom_mask()
        bottom_offset = (bottom_pos[0] - bird_rect.left, bottom_pos[1] - bird_rect.top)
        if bird_mask.overlap(bottom_mask, bottom_offset):
            return True

        return False


class Ground:
    """The scrolling ground at the bottom of the screen."""

    def __init__(self):
        self.image = load_sprite("base.png")
        self.width = self.image.get_width()
        self.y = GAME_HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = self.width

    def update(self, speed):
        self.x1 -= speed
        self.x2 -= speed
        if self.x1 < -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 < -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.image, (self.x1, self.y))
        screen.blit(self.image, (self.x2, self.y))

    def get_y(self):
        return self.y


class Background:
    """The scrolling background with day/night support."""

    def __init__(self):
        self.day_img = load_sprite("background-day.png")
        self.night_img = load_sprite("background-night.png")
        self.image = self.day_img
        self.width = self.image.get_width()
        self.x1 = 0
        self.x2 = self.width
        self.is_night = False

    def set_night(self, night):
        self.is_night = night
        self.image = self.night_img if night else self.day_img

    def toggle(self):
        self.set_night(not self.is_night)

    def update(self, speed):
        self.x1 -= speed // 2
        self.x2 -= speed // 2
        if self.x1 < -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 < -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.image, (self.x1, 0))
        screen.blit(self.image, (self.x2, 0))


class ScoreDisplay:
    """Handles rendering the score using number sprites."""

    def __init__(self):
        self.numbers = load_number_sprites()

    def draw(self, screen, score, y=50):
        score_str = str(score)
        digit_width = self.numbers[0].get_width()
        total_width = len(score_str) * digit_width
        x = (GAME_WIDTH - total_width) // 2

        for char in score_str:
            digit = int(char)
            screen.blit(self.numbers[digit], (x, y))
            x += digit_width


# ─── Main Game Class ─────────────────────────────────────────────────────────


class Game:
    """Main game class that manages game state and loop."""

    def __init__(self):
        # Create the display window at 2x scale
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird — Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True

        # Internal surface for rendering at native resolution (pixel-perfect)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Load sounds
        self.sounds = {
            "wing": load_sound("wing.wav"),
            "point": load_sound("point.wav"),
            "hit": load_sound("hit.wav"),
            "die": load_sound("die.wav"),
            "swoosh": load_sound("swoosh.wav"),
        }

        # Load UI images
        self.message_img = load_sprite("message.png")
        self.gameover_img = load_sprite("gameover.png")

        # Initialize game objects
        self.background = Background()
        self.ground = Ground()
        self.score_display = ScoreDisplay()

        # Settings
        self.difficulty = "NORMAL"
        self.bird_color_index = 0
        self.leaderboard = load_leaderboard()

        # Game state
        self.state = "START"  # START, PLAYING, PAUSED, GAME_OVER, LEADERBOARD
        self.bird = None
        self.pipes = []
        self.score = 0
        self.high_score = 0
        self.last_pipe_time = 0
        self.pipe_cycle = 0  # For day/night cycle

        # UI positions
        self.message_rect = self.message_img.get_rect(
            center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 40)
        )
        self.gameover_rect = self.gameover_img.get_rect(
            center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50)
        )

    def get_difficulty_settings(self):
        return DIFFICULTIES[self.difficulty]

    def reset(self):
        color = BIRD_COLORS[self.bird_color_index]
        self.bird = Bird(50, GAME_HEIGHT // 2, color=color)
        self.pipes = []
        self.score = 0
        self.pipe_cycle = 0
        settings = self.get_difficulty_settings()
        self.last_pipe_time = pygame.time.get_ticks()
        # Reset background to day at start
        self.background.set_night(False)

    def spawn_pipe(self):
        settings = self.get_difficulty_settings()
        min_gap = 80
        max_gap = GAME_HEIGHT - GROUND_HEIGHT - settings["gap"] - 50
        gap_y = random.randint(min_gap, max_gap)
        pipe = Pipe(GAME_WIDTH, gap_y, settings["gap"])
        self.pipes.append(pipe)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_p:
                    if self.state == "PLAYING":
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.state = "PLAYING"

                if event.key == pygame.K_n:
                    self.background.toggle()

                if event.key == pygame.K_c:
                    if self.state in ("START", "PAUSED"):
                        self.bird_color_index = (self.bird_color_index + 1) % len(BIRD_COLORS)
                        if self.bird:
                            self.bird.set_color(BIRD_COLORS[self.bird_color_index])

                if event.key == pygame.K_d:
                    if self.state in ("START", "PAUSED"):
                        diffs = list(DIFFICULTIES.keys())
                        idx = diffs.index(self.difficulty)
                        self.difficulty = diffs[(idx + 1) % len(diffs)]

                if event.key == pygame.K_l:
                    if self.state == "START":
                        self.state = "LEADERBOARD"
                    elif self.state == "LEADERBOARD":
                        self.state = "START"

                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.state in ("START", "PLAYING", "GAME_OVER"):
                        self.handle_flap()

                if event.key == pygame.K_r and self.state == "GAME_OVER":
                    self.state = "START"
                    self.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.state in ("START", "PLAYING", "GAME_OVER"):
                        self.handle_flap()

    def handle_flap(self):
        if self.state == "START":
            if self.sounds["swoosh"]:
                self.sounds["swoosh"].play()
            self.state = "PLAYING"
            self.reset()
            self.bird.flap()
        elif self.state == "PLAYING":
            if self.sounds["wing"]:
                self.sounds["wing"].play()
            self.bird.flap()
        elif self.state == "GAME_OVER":
            if self.sounds["swoosh"]:
                self.sounds["swoosh"].play()
            self.state = "START"
            self.reset()

    def update(self):
        settings = self.get_difficulty_settings()

        # Always scroll background and ground (even on start screen)
        self.background.update(settings["speed"])
        self.ground.update(settings["speed"])

        if self.state == "START":
            if self.bird is None:
                color = BIRD_COLORS[self.bird_color_index]
                self.bird = Bird(50, GAME_HEIGHT // 2, color=color)
            self.bird.animation_timer += 1
            if self.bird.animation_timer >= self.bird.animation_speed:
                self.bird.animation_timer = 0
                self.bird.frame_index = (self.bird.frame_index + 1) % len(self.bird.frames)
            self.bird.y = GAME_HEIGHT // 2 + int(10 * math.sin(pygame.time.get_ticks() / 300))

        elif self.state == "PLAYING":
            self.bird.update()

            # Ground collision
            if self.bird.y + self.bird.get_rect().height // 2 >= self.ground.get_y():
                self.game_over()
                return

            # Ceiling collision
            if self.bird.y - self.bird.get_rect().height // 2 <= 0:
                self.bird.y = self.bird.get_rect().height // 2
                self.bird.velocity = 0

            # Spawn pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe_time > settings["spawn"]:
                self.spawn_pipe()
                self.last_pipe_time = current_time

            # Update pipes
            for pipe in self.pipes:
                pipe.update(settings["speed"])

                if pipe.collides_with(self.bird):
                    self.game_over()
                    return

                if not pipe.passed and pipe.x + pipe.pipe_width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                    if self.sounds["point"]:
                        self.sounds["point"].play()

                    # Day/night cycle: toggle every 10 points
                    if self.score > 0 and self.score % 10 == 0:
                        self.background.toggle()

            # Remove off-screen pipes
            self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def game_over(self):
        self.state = "GAME_OVER"
        if self.sounds["hit"]:
            self.sounds["hit"].play()
        pygame.time.delay(200)
        if self.sounds["die"]:
            self.sounds["die"].play()
        if self.score > self.high_score:
            self.high_score = self.score
        self.leaderboard = add_score(
            self.leaderboard, self.score, self.difficulty, self.bird.color
        )
        save_leaderboard(self.leaderboard)

    def draw(self):
        # Clear the internal game surface
        self.game_surface.fill((0, 0, 0))

        # Draw background
        self.background.draw(self.game_surface)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.game_surface)

        # Draw ground
        self.ground.draw(self.game_surface)

        # Draw bird
        if self.bird:
            self.bird.draw(self.game_surface)

        # Draw UI based on state
        if self.state == "START":
            self.game_surface.blit(self.message_img, self.message_rect)
            self.draw_settings_overlay()

        elif self.state == "PLAYING":
            self.score_display.draw(self.game_surface, self.score)

        elif self.state == "PAUSED":
            self.score_display.draw(self.game_surface, self.score)
            self.draw_pause_overlay()

        elif self.state == "GAME_OVER":
            self.game_surface.blit(self.gameover_img, self.gameover_rect)
            self.score_display.draw(self.game_surface, self.score)
            self.draw_score_panel()

        elif self.state == "LEADERBOARD":
            self.draw_leaderboard()

        # Scale up to the main screen (2x for crisp pixel art)
        scaled = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    # ─── UI Overlays ─────────────────────────────────────────────────────────

    def draw_settings_overlay(self):
        """Draw difficulty and bird color info on the start screen."""
        settings = self.get_difficulty_settings()
        color = BIRD_COLORS[self.bird_color_index].capitalize()
        diff_label = settings["label"]

        y = GAME_HEIGHT - 80
        diff_surf = render_text(f"Difficulty: {diff_label}  (D to change)", 11, (255, 255, 255))
        color_surf = render_text(f"Bird: {color}  (C to change)", 11, (255, 255, 255))
        night_surf = render_text("N = Night mode | P = Pause | L = Leaderboard", 10, (200, 200, 200))

        self.game_surface.blit(diff_surf, (10, y))
        self.game_surface.blit(color_surf, (10, y + 16))
        self.game_surface.blit(night_surf, (10, y + 34))

    def draw_pause_overlay(self):
        """Draw the pause screen overlay."""
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.game_surface.blit(overlay, (0, 0))

        pause_text = render_text("PAUSED", 36, (255, 255, 255))
        rect = pause_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 20))
        self.game_surface.blit(pause_text, rect)

        hint = render_text("Press P to resume", 14, (200, 200, 200))
        hrect = hint.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 20))
        self.game_surface.blit(hint, hrect)

    def draw_score_panel(self):
        """Draw a score panel on game over screen."""
        panel_width = 200
        panel_height = 140
        panel_x = (GAME_WIDTH - panel_width) // 2
        panel_y = GAME_HEIGHT // 2 + 20

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (222, 216, 149, 200), (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surface, (133, 94, 32, 255), (0, 0, panel_width, panel_height), width=3, border_radius=10)
        self.game_surface.blit(panel_surface, (panel_x, panel_y))

        score_label = render_text("SCORE", 16, (255, 87, 34))
        score_value = render_text(str(self.score), 18, (255, 255, 255))
        best_label = render_text("BEST", 16, (255, 87, 34))
        best_value = render_text(str(self.high_score), 18, (255, 255, 255))
        diff_label = render_text(f"Mode: {self.get_difficulty_settings()['label']}", 12, (180, 180, 180))

        self.game_surface.blit(score_label, (panel_x + 20, panel_y + 15))
        self.game_surface.blit(score_value, (panel_x + 20, panel_y + 35))
        self.game_surface.blit(best_label, (panel_x + panel_width - 80, panel_y + 15))
        self.game_surface.blit(best_value, (panel_x + panel_width - 80, panel_y + 35))
        self.game_surface.blit(diff_label, (panel_x + 20, panel_y + 60))

        # Medal
        if self.score >= 10:
            medal_color = (255, 215, 0)
            medal_text = "GOLD"
        elif self.score >= 5:
            medal_color = (192, 192, 192)
            medal_text = "SILVER"
        elif self.score >= 1:
            medal_color = (205, 127, 50)
            medal_text = "BRONZE"
        else:
            medal_color = None

        if medal_color:
            pygame.draw.circle(self.game_surface, medal_color, (panel_x + panel_width // 2, panel_y + 100), 15)
            mt = render_text(medal_text, 10, (0, 0, 0))
            mt_rect = mt.get_rect(center=(panel_x + panel_width // 2, panel_y + 100))
            self.game_surface.blit(mt, mt_rect)

        # Restart hint
        hint = render_text("Press SPACE or Click to restart", 11, (255, 255, 255))
        hrect = hint.get_rect(center=(GAME_WIDTH // 2, panel_y + panel_height + 20))
        self.game_surface.blit(hint, hrect)

    def draw_leaderboard(self):
        """Draw the leaderboard screen."""
        self.game_surface.blit(self.message_img, self.message_rect)

        title = render_text("LEADERBOARD", 20, (255, 215, 0))
        trect = title.get_rect(center=(GAME_WIDTH // 2, 120))
        self.game_surface.blit(title, trect)

        if not self.leaderboard:
            empty = render_text("No scores yet!", 14, (200, 200, 200))
            erect = empty.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
            self.game_surface.blit(empty, erect)
        else:
            y = 160
            header = render_text("RANK  SCORE  MODE      BIRD", 12, (180, 180, 180))
            self.game_surface.blit(header, (30, y))
            y += 22

            for i, entry in enumerate(self.leaderboard[:10]):
                rank = f"{i+1:>4}."
                score = f"{entry['score']:>5}"
                mode = f"{entry['difficulty']:>8}"
                bird = entry.get("bird_color", "yellow").capitalize()
                line = render_text(f"{rank}  {score}  {mode}  {bird}", 13, (255, 255, 255))
                self.game_surface.blit(line, (30, y))
                y += 20

        hint = render_text("Press L to go back", 12, (200, 200, 200))
        hrect = hint.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 40))
        self.game_surface.blit(hint, hrect)

    # ─── Main Loop ───────────────────────────────────────────────────────────

    def run(self):
        self.reset()
        self.bird.y = GAME_HEIGHT // 2

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
