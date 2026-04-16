import pygame


class Ball:
    def __init__(self, x, y, radius, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.step = 20  # movement per key press

    def move_up(self):
        if self.y - self.step - self.radius >= 0:
            self.y -= self.step

    def move_down(self):
        if self.y + self.step + self.radius <= self.screen_height:
            self.y += self.step

    def move_left(self):
        if self.x - self.step - self.radius >= 0:
            self.x -= self.step

    def move_right(self):
        if self.x + self.step + self.radius <= self.screen_width:
            self.x += self.step

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)