import pygame


class Button:
    """Simple button class for Pygame screens."""

    def __init__(self, x, y, w, h, text, font, bg=(70, 70, 70), fg=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = (100, 100, 100) if self.rect.collidepoint(mouse_pos) else self.bg

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, self.fg)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_text(screen, text, font, color, x, y, center=False):
    """Draw text on screen."""
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)
