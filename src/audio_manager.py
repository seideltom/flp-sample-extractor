import pygame
import os

class AudioManager:
    def __init__(self):
        self.current_audio_path = None
        self.audio = None
        self.channel = None
    
    def play_audio(self, audio_path):
        self.stop_audio()

        if not os.path.exists(audio_path):
            print(f"Audio file does not exist: {audio_path}")
            return

        if self.current_audio_path != audio_path:
            self.load_audio(audio_path)

        if self.audio:
            self.channel = self.audio.play()


    def load_audio(self, audio_path):
        try:
            self.audio = pygame.mixer.Sound(audio_path)
            self.current_audio_path = audio_path

        except pygame.error as e:
            print(f"Error loading audio file: {e}")
            self.audio = None


    def stop_audio(self):
        if self.channel and self.channel.get_busy():
            self.channel.stop()
