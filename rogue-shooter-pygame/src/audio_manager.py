"""Audio manager"""
import pygame
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")


class AudioManager:
    def __init__(self):
        self.sfx = {}
        self.music = {}
        self.current_music = None
        self.mixer_available = False
        try:
            import pygame.mixer
            if pygame.mixer.get_init() is not None:
                self.mixer_available = True
        except Exception:
            pass
        if self.mixer_available:
            self._load()
    
    def _load(self):
        try:
            sfx_dir = os.path.join(AUDIO_DIR, "sfx")
            for fname in os.listdir(sfx_dir):
                if fname.lower().endswith('.wav'):
                    key = fname.replace('.wav', '').replace(' ', '_').lower()
                    path = os.path.join(sfx_dir, fname)
                    self.sfx[key] = pygame.mixer.Sound(path)
        except Exception:
            pass
        
        try:
            music_dir = os.path.join(AUDIO_DIR, "music")
            for fname in os.listdir(music_dir):
                if fname.lower().endswith('.wav'):
                    key = fname.replace('.wav', '').replace(' ', '_').lower()
                    path = os.path.join(music_dir, fname)
                    self.music[key] = path
        except Exception:
            pass
    
    def play_sfx(self, name, volume=0.5):
        if not self.mixer_available:
            return
        sound = self.sfx.get(name.lower())
        if sound:
            sound.set_volume(volume)
            sound.stop()
            sound.play()
    
    def play_music(self, name, loops=-1, volume=0.4):
        if not self.mixer_available:
            return
        key = name.lower().replace(' ', '_')
        path = self.music.get(key)
        if path:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                self.current_music = key
            except Exception:
                pass
    
    def stop_music(self):
        if not self.mixer_available:
            return
        pygame.mixer.music.stop()
