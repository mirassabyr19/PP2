import pygame
import os


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()

        self.base_path = os.path.dirname(__file__)
        self.music_path = os.path.join(self.base_path, "music")

        self.playlist = []
        for file_name in os.listdir(self.music_path):
            if file_name.endswith(".mp3") or file_name.endswith(".wav"):
                full_path = os.path.join(self.music_path, file_name)
                self.playlist.append(full_path)

        self.playlist.sort()

        self.current_index = 0
        self.is_playing = False
        self.track_start_time = 0

    def load_current_track(self):
        if len(self.playlist) == 0:
            return

        pygame.mixer.music.load(self.playlist[self.current_index])

    def play(self):
        if len(self.playlist) == 0:
            return

        self.load_current_track()
        pygame.mixer.music.play()
        self.is_playing = True
        self.track_start_time = pygame.time.get_ticks()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if len(self.playlist) == 0:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        if len(self.playlist) == 0:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_current_track_name(self):
        if len(self.playlist) == 0:
            return "No tracks found"

        return os.path.basename(self.playlist[self.current_index])

    def get_progress_seconds(self):
        if not self.is_playing:
            return 0

        current_time = pygame.time.get_ticks()
        return (current_time - self.track_start_time) // 1000