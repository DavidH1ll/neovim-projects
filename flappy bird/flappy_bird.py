#!/usr/bin/env python3
"""
Flappy Bird Clone

A pygame-based clone of the classic Flappy Bird game.
Built while learning Neovim.

Assets: https://github.com/samuelcust/flappy-bird-assets
"""

import math
import os
import random
import sys

import pygame
from PIL import Image

# Initialize pygame
pygame.init()

# Try to initialize audio, but allow the game to run without it
AUDIO_AVAILABLE = False
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except (pygame.error, NotImplementedError):
    print("Warning: Audio not available. Game will run without sound.")
    AUDIO_AVAILABLE = False

# Check font availability
FONT_AVAILABLE = False
try:
    pygame.font.init()
    FONT_AVAILABLE = True
except (pygame.error, NotImplementedError):
    print("Warning: Font rendering not available. Using fallback.")

# Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60

# Game physics
GRAVITY = 0.25
FLAP_STRENGTH = -4.5
PIPE_GAP = 100
PIPE_SPAWN_INTERVAL = 1200  # milliseconds
GROUND_HEIGHT = 112
SCROLL_SPEED = 2

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")


def load_sprite(name):
    """Load a sprite image from the assets directory."""
    path = os.path.join(SPRITES_DIR, name)
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error:
        # Fallback: Use Pillow for PNG support
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


class Bird:
    """The player-controlled bird."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.rotation = 0

        # Load bird animation frames (yellow bird)
        self.frames = [
            load_sprite("yellowbird-downflap.png"),
            load_sprite("yellowbird-midflap.png"),
            load_sprite("yellowbird-upflap.png"),
        ]
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 5  # frames between animation changes

    def update(self):
        """Update bird physics and animation."""
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity

        # Update rotation based on velocity
        if self.velocity < 0:
            self.rotation = max(self.rotation - 3, -25)
        else:
            self.rotation = min(self.rotation + 3, 90)

        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def flap(self):
        """Make the bird jump."""
        self.velocity = FLAP_STRENGTH
        self.rotation = -25

    def draw(self, screen):
        """Draw the bird with rotation."""
        frame = self.frames[self.frame_index]
        rotated = pygame.transform.rotate(frame, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

    def get_mask(self):
        """Get a collision mask for the bird."""
        frame = self.frames[self.frame_index]
        return pygame.mask.from_surface(frame)

    def get_rect(self):
        """Get the bounding rectangle of the bird."""
        frame = self.frames[self.frame_index]
        rect = frame.get_rect(center=(self.x, self.y))
        return rect


class Pipe:
    """A pair of pipes (top and bottom) that the bird must fly through."""

    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.passed = False

        self.pipe_img = load_sprite("pipe-green.png")
        self.pipe_width = self.pipe_img.get_width()
        self.pipe_height = self.pipe_img.get_height()

        # Top pipe (flipped)
        self.top_pipe = pygame.transform.flip(self.pipe_img, False, True)
        self.top_y = gap_y - PIPE_GAP // 2 - self.pipe_height

        # Bottom pipe
        self.bottom_y = gap_y + PIPE_GAP // 2

    def update(self):
        """Move the pipe to the left."""
        self.x -= SCROLL_SPEED

    def draw(self, screen):
        """Draw both pipes."""
        screen.blit(self.top_pipe, (self.x, self.top_y))
        screen.blit(self.pipe_img, (self.x, self.bottom_y))

    def is_off_screen(self):
        """Check if the pipe has moved off the left side of the screen."""
        return self.x < -self.pipe_width

    def get_top_mask(self):
        """Get collision mask for the top pipe."""
        mask = pygame.mask.from_surface(self.top_pipe)
        return mask, (self.x, self.top_y)

    def get_bottom_mask(self):
        """Get collision mask for the bottom pipe."""
        mask = pygame.mask.from_surface(self.pipe_img)
        return mask, (self.x, self.bottom_y)

    def collides_with(self, bird):
        """Check if the bird collides with either pipe."""
        bird_mask = bird.get_mask()
        bird_rect = bird.get_rect()

        # Check top pipe
        top_mask, top_pos = self.get_top_mask()
        top_offset = (top_pos[0] - bird_rect.left, top_pos[1] - bird_rect.top)
        if bird_mask.overlap(top_mask, top_offset):
            return True

        # Check bottom pipe
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
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = self.width

    def update(self):
        """Scroll the ground."""
        self.x1 -= SCROLL_SPEED
        self.x2 -= SCROLL_SPEED

        if self.x1 < -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 < -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        """Draw the scrolling ground."""
        screen.blit(self.image, (self.x1, self.y))
        screen.blit(self.image, (self.x2, self.y))

    def get_y(self):
        """Get the Y position of the ground top."""
        return self.y


class Background:
    """The scrolling background."""

    def __init__(self):
        self.image = load_sprite("background-day.png")
        self.width = self.image.get_width()
        self.x1 = 0
        self.x2 = self.width

    def update(self):
        """Scroll the background (slower than ground)."""
        self.x1 -= SCROLL_SPEED // 2
        self.x2 -= SCROLL_SPEED // 2

        if self.x1 < -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 < -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        """Draw the scrolling background."""
        screen.blit(self.image, (self.x1, 0))
        screen.blit(self.image, (self.x2, 0))


class ScoreDisplay:
    """Handles rendering the score using number sprites."""

    def __init__(self):
        self.numbers = load_number_sprites()

    def draw(self, screen, score):
        """Draw the score centered at the top of the screen."""
        score_str = str(score)
        digit_width = self.numbers[0].get_width()
        digit_height = self.numbers[0].get_height()
        total_width = len(score_str) * digit_width
        x = (SCREEN_WIDTH - total_width) // 2
        y = 50

        for char in score_str:
            digit = int(char)
            screen.blit(self.numbers[digit], (x, y))
            x += digit_width


class Game:
    """Main game class that manages game state and loop."""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.running = True

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

        # Game state
        self.state = "START"  # START, PLAYING, GAME_OVER
        self.bird = None
        self.pipes = []
        self.score = 0
        self.high_score = 0
        self.last_pipe_time = 0

        # Message position
        self.message_rect = self.message_img.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        )
        self.gameover_rect = self.gameover_img.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        )

    def reset(self):
        """Reset the game state for a new round."""
        self.bird = Bird(50, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.last_pipe_time = pygame.time.get_ticks()

    def spawn_pipe(self):
        """Spawn a new pair of pipes."""
        min_gap = 100
        max_gap = SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 50
        gap_y = random.randint(min_gap, max_gap)
        pipe = Pipe(SCREEN_WIDTH, gap_y)
        self.pipes.append(pipe)

    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.handle_flap()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r and self.state == "GAME_OVER":
                    self.state = "START"
                    self.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_flap()

    def handle_flap(self):
        """Handle flap action based on game state."""
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
        """Update game logic."""
        # Always scroll background and ground
        self.background.update()
        self.ground.update()

        if self.state == "START":
            # Animate bird floating
            if self.bird is None:
                self.bird = Bird(50, SCREEN_HEIGHT // 2)
            self.bird.animation_timer += 1
            if self.bird.animation_timer >= self.bird.animation_speed:
                self.bird.animation_timer = 0
                self.bird.frame_index = (self.bird.frame_index + 1) % len(self.bird.frames)
            # Gentle floating motion
            self.bird.y = SCREEN_HEIGHT // 2 + int(10 * math.sin(pygame.time.get_ticks() / 300))

        elif self.state == "PLAYING":
            self.bird.update()

            # Check ground collision
            if self.bird.y + self.bird.get_rect().height // 2 >= self.ground.get_y():
                self.game_over()
                return

            # Check ceiling collision
            if self.bird.y - self.bird.get_rect().height // 2 <= 0:
                self.bird.y = self.bird.get_rect().height // 2
                self.bird.velocity = 0

            # Spawn pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe_time > PIPE_SPAWN_INTERVAL:
                self.spawn_pipe()
                self.last_pipe_time = current_time

            # Update pipes
            for pipe in self.pipes:
                pipe.update()

                # Check collision
                if pipe.collides_with(self.bird):
                    self.game_over()
                    return

                # Check if bird passed the pipe
                if not pipe.passed and pipe.x + pipe.pipe_width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                    if self.sounds["point"]:
                        self.sounds["point"].play()

            # Remove off-screen pipes
            self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def game_over(self):
        """Handle game over state."""
        self.state = "GAME_OVER"
        if self.sounds["hit"]:
            self.sounds["hit"].play()
        pygame.time.delay(200)
        if self.sounds["die"]:
            self.sounds["die"].play()
        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        """Render the game."""
        self.screen.fill((0, 0, 0))

        # Draw background
        self.background.draw(self.screen)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Draw ground
        self.ground.draw(self.screen)

        # Draw bird
        if self.bird:
            self.bird.draw(self.screen)

        # Draw UI based on state
        if self.state == "START":
            self.screen.blit(self.message_img, self.message_rect)

        elif self.state == "PLAYING":
            self.score_display.draw(self.screen, self.score)

        elif self.state == "GAME_OVER":
            self.screen.blit(self.gameover_img, self.gameover_rect)
            self.score_display.draw(self.screen, self.score)
            self.draw_score_panel()

        pygame.display.flip()

    def render_text(self, text, size, color, bold=True):
        """Render text to a pygame surface, with Pillow fallback."""
        if FONT_AVAILABLE:
            font = pygame.font.SysFont("Arial", size, bold=bold)
            return font.render(text, True, color)
        else:
            # Fallback: use Pillow
            from PIL import ImageDraw, ImageFont
            try:
                pil_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            except:
                pil_font = ImageFont.load_default()
            bbox = pil_font.getbbox(text)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((0, -bbox[1]), text, font=pil_font, fill=color)
            return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")

    def draw_score_panel(self):
        """Draw a score panel on game over screen."""
        panel_width = 200
        panel_height = 120
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = SCREEN_HEIGHT // 2 + 20

        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (222, 216, 149, 200), (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surface, (133, 94, 32, 255), (0, 0, panel_width, panel_height), width=3, border_radius=10)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Draw text
        score_label = self.render_text("SCORE", 18, (255, 87, 34))
        score_value = self.render_text(str(self.score), 18, (255, 255, 255))
        best_label = self.render_text("BEST", 18, (255, 87, 34))
        best_value = self.render_text(str(self.high_score), 18, (255, 255, 255))

        self.screen.blit(score_label, (panel_x + 20, panel_y + 20))
        self.screen.blit(score_value, (panel_x + 20, panel_y + 45))
        self.screen.blit(best_label, (panel_x + panel_width - 80, panel_y + 20))
        self.screen.blit(best_value, (panel_x + panel_width - 80, panel_y + 45))

        # Medal based on score
        if self.score >= 10:
            medal_color = (255, 215, 0)  # Gold
            medal_text = "GOLD"
        elif self.score >= 5:
            medal_color = (192, 192, 192)  # Silver
            medal_text = "SILVER"
        elif self.score >= 1:
            medal_color = (205, 127, 50)  # Bronze
            medal_text = "BRONZE"
        else:
            medal_color = None

        if medal_color:
            pygame.draw.circle(self.screen, medal_color, (panel_x + panel_width // 2, panel_y + 90), 15)
            mt = self.render_text(medal_text, 10, (0, 0, 0))
            mt_rect = mt.get_rect(center=(panel_x + panel_width // 2, panel_y + 90))
            self.screen.blit(mt, mt_rect)

    def run(self):
        """Main game loop."""
        self.reset()
        self.bird.y = SCREEN_HEIGHT // 2  # Reset bird position for start screen

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
