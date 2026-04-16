import pygame
import datetime
import os
import math


def blit_rotate(surface, image, pivot, angle, offset):
    """
    Rotate an image around a pivot point.
    """
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_offset = offset.rotate(-angle)

    rect = rotated_image.get_rect(
        center=(pivot[0] + rotated_offset.x,
                pivot[1] + rotated_offset.y)
    )

    surface.blit(rotated_image, rect)


def draw_clock_face(screen, center, radius):
    """
    Draw clock circle and ticks
    """
    pygame.draw.circle(screen, (240, 240, 240), center, radius)
    pygame.draw.circle(screen, (40, 40, 40), center, radius, 4)

    for i in range(60):
        angle = math.radians(i * 6 - 90)

        outer_x = center[0] + math.cos(angle) * radius
        outer_y = center[1] + math.sin(angle) * radius

        if i % 5 == 0:
            inner_radius = radius - 20
            width = 4
        else:
            inner_radius = radius - 10
            width = 2

        inner_x = center[0] + math.cos(angle) * inner_radius
        inner_y = center[1] + math.sin(angle) * inner_radius

        pygame.draw.line(screen, (40, 40, 40),
                         (inner_x, inner_y), (outer_x, outer_y), width)

    pygame.draw.circle(screen, (40, 40, 40), center, 6)


def draw_numbers(screen, center, radius, font):
    """
    Draw numbers 1–12 on the clock
    """
    for i in range(1, 13):
        angle = math.radians(i * 30 - 90)

        x = center[0] + math.cos(angle) * (radius - 40)
        y = center[1] + math.sin(angle) * (radius - 40)

        text = font.render(str(i), True, (0, 0, 0))
        rect = text.get_rect(center=(x, y))

        screen.blit(text, rect)


def run_clock():
    pygame.init()

    WIDTH = 800
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey Clock")

    clock = pygame.time.Clock()

    # Paths
    base_path = os.path.dirname(__file__)
    images_path = os.path.join(base_path, "images")

    # Load hand image
    hand_img = pygame.image.load(
        os.path.join(images_path, "mickey_hand.png")
    ).convert_alpha()

    # Resize hand
    hand_img = pygame.transform.smoothscale(hand_img, (120, 220))

    center = (WIDTH // 2, HEIGHT // 2)
    radius = 230

    # Offsets (adjust if needed)
    minutes_offset = pygame.math.Vector2(0, -60)
    seconds_offset = pygame.math.Vector2(0, -90)

    # Font for numbers and time
    font = pygame.font.SysFont("arial", 28, bold=True)
    time_font = pygame.font.SysFont("arial", 36, bold=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # Angles
        seconds_angle = -(seconds * 6)
        minutes_angle = -(minutes * 6 + seconds * 0.1)

        # Background
        screen.fill((220, 220, 220))

        # Draw clock
        draw_clock_face(screen, center, radius)
        draw_numbers(screen, center, radius, font)

        # Draw hands
        blit_rotate(screen, hand_img, center, minutes_angle, minutes_offset)
        blit_rotate(screen, hand_img, center, seconds_angle, seconds_offset)

        # Digital time on top
        time_text = time_font.render(f"{minutes:02d}:{seconds:02d}", True, (20, 20, 20))
        text_rect = time_text.get_rect(center=(WIDTH // 2, 40))
        screen.blit(time_text, text_rect)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()