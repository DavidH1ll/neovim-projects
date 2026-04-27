"""Particle and effect system"""
import pygame
import random
import math
from settings import SCALE


class Particle:
    def __init__(self, x, y, vx, vy, life, color=None, image=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.image = image
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-10, 10)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.angle += self.rot_speed
    
    def draw(self, surf, cx, cy):
        if self.life <= 0:
            return
        alpha = self.life / self.max_life
        px = int(self.x + cx)
        py = int(self.y + cy)
        if self.image:
            img = self.image
            if alpha < 1:
                img = img.copy()
                img.set_alpha(int(alpha * 255))
            rect = img.get_rect(center=(px, py))
            surf.blit(img, rect)
        elif self.color:
            size = max(1, int(2 * alpha * SCALE))
            pygame.draw.rect(surf, self.color, (px - size//2, py - size//2, size, size))


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def clear(self):
        self.particles.clear()
    
    def spawn_hit(self, x, y, color=(255, 255, 200), count=5):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, random.randint(10, 20), color=color))
    
    def spawn_explosion(self, x, y, color=(255, 100, 50), count=15):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, random.randint(20, 40), color=color))
    
    def spawn_splatter(self, x, y, images):
        if images:
            img = random.choice(images)
            angle = random.choice([0, 90, 180, 270])
            if angle != 0:
                img = pygame.transform.rotate(img, angle)
            self.particles.append(Particle(x, y, 0, 0, 300, image=img))
    
    def spawn_broken_pieces(self, x, y, images, count=4):
        if images:
            for _ in range(min(count, len(images))):
                img = random.choice(images)
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 3)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                p = Particle(x, y, vx, vy, random.randint(30, 60), image=img)
                p.rot_speed = random.uniform(-15, 15)
                self.particles.append(p)
    
    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
    
    def draw(self, surf, cx, cy):
        for p in self.particles:
            p.draw(surf, cx, cy)
