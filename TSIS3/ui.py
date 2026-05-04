import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 130, 255)


class Button:
    """Simple button class for Pygame screens."""
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, screen):
        """Draw the button with hover effect."""
        mouse_pos = pygame.mouse.get_pos()
        color = BLUE if self.rect.collidepoint(mouse_pos) else GRAY

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Return True if user clicked this button."""
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
