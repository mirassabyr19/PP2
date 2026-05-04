"""Helper functions and UI classes for TSIS 2 Paint Application."""

from __future__ import annotations

from collections import deque
from datetime import datetime
import os
import math
from typing import Iterable, Tuple

import pygame


Color = Tuple[int, int, int]
Point = Tuple[int, int]

WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)
DARK_GRAY: Color = (35, 35, 35)
LIGHT_GRAY: Color = (210, 210, 210)
BLUE: Color = (60, 120, 255)


class Button:
    """Simple rectangular toolbar button."""

    def __init__(self, rect: pygame.Rect, text: str, value: str, kind: str):
        self.rect = rect
        self.text = text
        self.value = value
        self.kind = kind

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, active: bool = False) -> None:
        fill_color = BLUE if active else LIGHT_GRAY
        text_color = WHITE if active else BLACK
        pygame.draw.rect(surface, fill_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, self.rect, width=1, border_radius=6)
        label = font.render(self.text, True, text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def is_clicked(self, pos: Point) -> bool:
        return self.rect.collidepoint(pos)


def normalize_rect(start: Point, end: Point) -> pygame.Rect:
    """Create a positive-width rectangle from two corner points."""
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def square_rect(start: Point, end: Point) -> pygame.Rect:
    """Create a square rectangle from start point to current mouse position."""
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    side = min(abs(dx), abs(dy))
    x = x1 if dx >= 0 else x1 - side
    y = y1 if dy >= 0 else y1 - side
    return pygame.Rect(x, y, side, side)


def right_triangle_points(start: Point, end: Point) -> list[Point]:
    """Return three points for a right triangle inside the drag box."""
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(start: Point, end: Point) -> list[Point]:
    """Return points for an equilateral-style triangle based on drag width."""
    x1, y1 = start
    x2, y2 = end
    width = x2 - x1
    direction = 1 if y2 >= y1 else -1
    height = int(abs(width) * math.sqrt(3) / 2) * direction
    top = (x1 + width // 2, y1)
    left = (x1, y1 + height)
    right = (x2, y1 + height)
    return [top, left, right]


def rhombus_points(start: Point, end: Point) -> list[Point]:
    """Return four points for a rhombus inside the drag box."""
    rect = normalize_rect(start, end)
    cx, cy = rect.center
    return [
        (cx, rect.top),
        (rect.right, cy),
        (cx, rect.bottom),
        (rect.left, cy),
    ]


def draw_shape(
    surface: pygame.Surface,
    tool: str,
    start: Point,
    end: Point,
    color: Color,
    brush_size: int,
) -> None:
    """Draw one of the supported shape tools onto a surface."""
    if tool == "line":
        pygame.draw.line(surface, color, start, end, brush_size)

    elif tool == "rect":
        pygame.draw.rect(surface, color, normalize_rect(start, end), width=brush_size)

    elif tool == "circle":
        radius = int(math.dist(start, end))
        if radius > 0:
            pygame.draw.circle(surface, color, start, radius, width=brush_size)

    elif tool == "square":
        pygame.draw.rect(surface, color, square_rect(start, end), width=brush_size)

    elif tool == "right_triangle":
        pygame.draw.polygon(surface, color, right_triangle_points(start, end), width=brush_size)

    elif tool == "equilateral_triangle":
        pygame.draw.polygon(surface, color, equilateral_triangle_points(start, end), width=brush_size)

    elif tool == "rhombus":
        pygame.draw.polygon(surface, color, rhombus_points(start, end), width=brush_size)


def flood_fill(surface: pygame.Surface, start_pos: Point, new_color: Color) -> None:
    """Fill connected pixels with exact target color using get_at() and set_at()."""
    width, height = surface.get_size()
    x, y = start_pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    replacement = pygame.Color(new_color[0], new_color[1], new_color[2], 255)

    if target_color == replacement:
        return

    queue: deque[Point] = deque([(x, y)])

    while queue:
        px, py = queue.popleft()

        if not (0 <= px < width and 0 <= py < height):
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), replacement)
        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas(surface: pygame.Surface, folder: str = "saves") -> str:
    """Save the canvas as a timestamped PNG file and return the path."""
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"paint_{timestamp}.png")
    pygame.image.save(surface, filename)
    return filename
