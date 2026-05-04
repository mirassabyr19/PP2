"""TSIS 2: Paint Application — Extended Drawing Tools.

Controls:
P Pencil, L Line, R Rectangle, C Circle, E Eraser, F Fill, T Text,
Q Square, Y Right triangle, U Equilateral triangle, H Rhombus, I Color picker.
1/2/3 change brush size. Ctrl+S saves the canvas as PNG.
"""

import sys
import pygame

from tools import Button, WHITE, BLACK, DARK_GRAY, LIGHT_GRAY, BLUE
from tools import draw_shape, flood_fill, save_canvas


pygame.init()
pygame.font.init()

# Window and canvas settings
SCREEN_W = 1000
SCREEN_H = 700
TOOLBAR_W = 220
CANVAS_W = SCREEN_W - TOOLBAR_W
CANVAS_H = SCREEN_H
FPS = 60

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("TSIS 2 Paint Application")
clock = pygame.time.Clock()

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)

font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 15)
text_font = pygame.font.SysFont("arial", 28)

# Application state
current_tool = "pencil"
current_color = BLACK
brush_size = 5
start_pos = None
last_pos = None
is_dragging = False
status_message = "Ready"

# Text tool state
text_active = False
text_pos = None
text_buffer = ""

# Tools from Practice 10-11 plus new TSIS2 tools
TOOL_BUTTONS = [
    ("Pencil", "pencil"),
    ("Line", "line"),
    ("Rect", "rect"),
    ("Circle", "circle"),
    ("Eraser", "eraser"),
    ("Fill", "fill"),
    ("Text", "text"),
    ("Picker", "picker"),
    ("Square", "square"),
    ("Right Tri", "right_triangle"),
    ("Equi Tri", "equilateral_triangle"),
    ("Rhombus", "rhombus"),
]

BRUSH_BUTTONS = [("2 px", "2"), ("5 px", "5"), ("10 px", "10")]

PALETTE = [
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 180, 0),
    (0, 0, 255),
    (255, 220, 0),
    (255, 140, 0),
    (140, 0, 180),
    (0, 200, 200),
    (255, 0, 180),
    (120, 70, 20),
    (130, 130, 130),
]

buttons = []

# Create tool buttons
x = 15
y = 45
button_w = 90
button_h = 30
for index, (label, value) in enumerate(TOOL_BUTTONS):
    col = index % 2
    row = index // 2
    rect = pygame.Rect(x + col * 100, y + row * 38, button_w, button_h)
    buttons.append(Button(rect, label, value, "tool"))

# Create brush size buttons
brush_y = 315
for index, (label, value) in enumerate(BRUSH_BUTTONS):
    rect = pygame.Rect(15 + index * 65, brush_y, 58, 30)
    buttons.append(Button(rect, label, value, "brush"))

# Color palette rectangles
color_rects = []
palette_y = 400
for index, color in enumerate(PALETTE):
    col = index % 4
    row = index // 4
    rect = pygame.Rect(18 + col * 46, palette_y + row * 42, 34, 34)
    color_rects.append((rect, color))

save_button = Button(pygame.Rect(15, 555, 190, 34), "Save Ctrl+S", "save", "action")
clear_button = Button(pygame.Rect(15, 595, 190, 34), "Clear Canvas", "clear", "action")


def inside_canvas(screen_pos):
    """Check whether the mouse position is inside the drawing canvas."""
    x, y = screen_pos
    return TOOLBAR_W <= x < SCREEN_W and 0 <= y < SCREEN_H


def to_canvas_pos(screen_pos):
    """Convert screen coordinates to canvas coordinates."""
    x, y = screen_pos
    return x - TOOLBAR_W, y


def to_screen_pos(canvas_pos):
    """Convert canvas coordinates to screen coordinates."""
    x, y = canvas_pos
    return x + TOOLBAR_W, y


def set_tool(tool_name):
    """Change the active tool and cancel unfinished text input if needed."""
    global current_tool, text_active, text_buffer, text_pos
    current_tool = tool_name
    if tool_name != "text":
        text_active = False
        text_buffer = ""
        text_pos = None


def handle_keyboard(event):
    """Handle keyboard shortcuts and text input."""
    global current_tool, brush_size, status_message, text_active, text_buffer, text_pos

    keys = pygame.key.get_pressed()

    # Ctrl+S saves the canvas as a timestamped PNG file.
    if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        if event.key == pygame.K_s:
            path = save_canvas(canvas)
            status_message = f"Saved: {path}"
        return

    # Text mode captures letters until Enter or Escape.
    if text_active:
        if event.key == pygame.K_RETURN:
            if text_buffer.strip():
                rendered = text_font.render(text_buffer, True, current_color)
                canvas.blit(rendered, text_pos)
            text_active = False
            text_buffer = ""
            text_pos = None
            status_message = "Text placed"
        elif event.key == pygame.K_ESCAPE:
            text_active = False
            text_buffer = ""
            text_pos = None
            status_message = "Text cancelled"
        elif event.key == pygame.K_BACKSPACE:
            text_buffer = text_buffer[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                text_buffer += event.unicode
        return

    # Tool shortcuts
    shortcuts = {
        pygame.K_p: "pencil",
        pygame.K_l: "line",
        pygame.K_r: "rect",
        pygame.K_c: "circle",
        pygame.K_e: "eraser",
        pygame.K_f: "fill",
        pygame.K_t: "text",
        pygame.K_i: "picker",
        pygame.K_q: "square",
        pygame.K_y: "right_triangle",
        pygame.K_u: "equilateral_triangle",
        pygame.K_h: "rhombus",
    }

    if event.key in shortcuts:
        set_tool(shortcuts[event.key])
        status_message = f"Tool: {current_tool}"

    # Brush size shortcuts
    if event.key == pygame.K_1:
        brush_size = 2
        status_message = "Brush size: 2 px"
    elif event.key == pygame.K_2:
        brush_size = 5
        status_message = "Brush size: 5 px"
    elif event.key == pygame.K_3:
        brush_size = 10
        status_message = "Brush size: 10 px"


def handle_toolbar_click(pos):
    """Handle clicks on toolbar buttons and color palette."""
    global current_color, brush_size, status_message

    for button in buttons:
        if button.is_clicked(pos):
            if button.kind == "tool":
                set_tool(button.value)
                status_message = f"Tool: {current_tool}"
            elif button.kind == "brush":
                brush_size = int(button.value)
                status_message = f"Brush size: {brush_size} px"
            return True

    for rect, color in color_rects:
        if rect.collidepoint(pos):
            current_color = color
            status_message = f"Color selected: {color}"
            return True

    if save_button.is_clicked(pos):
        path = save_canvas(canvas)
        status_message = f"Saved: {path}"
        return True

    if clear_button.is_clicked(pos):
        canvas.fill(WHITE)
        status_message = "Canvas cleared"
        return True

    return False


def draw_toolbar():
    """Draw the toolbar, active tool information, brush buttons, and color palette."""
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, TOOLBAR_W, SCREEN_H))

    title = font.render("TSIS2 Paint", True, WHITE)
    screen.blit(title, (15, 12))

    for button in buttons:
        active = False
        if button.kind == "tool" and button.value == current_tool:
            active = True
        if button.kind == "brush" and int(button.value) == brush_size:
            active = True
        button.draw(screen, small_font, active)

    label = font.render("Colors", True, WHITE)
    screen.blit(label, (15, 370))

    for rect, color in color_rects:
        pygame.draw.rect(screen, color, rect)
        border_width = 4 if color == current_color else 1
        pygame.draw.rect(screen, WHITE, rect, width=border_width)
        pygame.draw.rect(screen, BLACK, rect, width=1)

    save_button.draw(screen, small_font, False)
    clear_button.draw(screen, small_font, False)

    info_lines = [
        f"Tool: {current_tool}",
        f"Brush: {brush_size}px",
        "Keys: P L R C E F T",
        "1/2/3 size, Ctrl+S save",
        status_message[:26],
    ]

    info_y = 640
    for line in info_lines:
        rendered = small_font.render(line, True, WHITE)
        screen.blit(rendered, (15, info_y))
        info_y += 18


def draw_text_preview():
    """Show real-time text preview and cursor before confirming with Enter."""
    if text_active and text_pos is not None:
        preview_text = text_buffer + "|"
        rendered = text_font.render(preview_text, True, current_color)
        screen.blit(rendered, to_screen_pos(text_pos))


def draw_canvas_border():
    """Draw a border around the drawing area."""
    pygame.draw.line(screen, BLACK, (TOOLBAR_W, 0), (TOOLBAR_W, SCREEN_H), 2)


def main():
    global start_pos, last_pos, is_dragging, current_color, status_message
    global text_active, text_pos, text_buffer

    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(canvas, (TOOLBAR_W, 0))

        # Live preview for line and shape tools.
        if is_dragging and start_pos is not None and inside_canvas(mouse_pos):
            preview_tools = {
                "line",
                "rect",
                "circle",
                "square",
                "right_triangle",
                "equilateral_triangle",
                "rhombus",
            }
            if current_tool in preview_tools:
                draw_shape(
                    screen,
                    current_tool,
                    to_screen_pos(start_pos),
                    mouse_pos,
                    current_color,
                    brush_size,
                )

        draw_text_preview()
        draw_canvas_border()
        draw_toolbar()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                handle_keyboard(event)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[0] < TOOLBAR_W:
                    handle_toolbar_click(event.pos)
                    continue

                if not inside_canvas(event.pos):
                    continue

                canvas_pos = to_canvas_pos(event.pos)

                if current_tool == "pencil":
                    is_dragging = True
                    last_pos = canvas_pos
                    pygame.draw.circle(canvas, current_color, canvas_pos, max(1, brush_size // 2))

                elif current_tool == "eraser":
                    is_dragging = True
                    last_pos = canvas_pos
                    pygame.draw.circle(canvas, WHITE, canvas_pos, max(1, brush_size // 2))

                elif current_tool == "fill":
                    flood_fill(canvas, canvas_pos, current_color)
                    status_message = "Area filled"

                elif current_tool == "picker":
                    picked = canvas.get_at(canvas_pos)
                    current_color = (picked.r, picked.g, picked.b)
                    status_message = f"Picked color: {current_color}"

                elif current_tool == "text":
                    text_active = True
                    text_pos = canvas_pos
                    text_buffer = ""
                    status_message = "Type text, Enter confirm, Esc cancel"

                else:
                    is_dragging = True
                    start_pos = canvas_pos

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging and pygame.mouse.get_pressed()[0] and inside_canvas(event.pos):
                    canvas_pos = to_canvas_pos(event.pos)

                    if current_tool == "pencil" and last_pos is not None:
                        pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size)
                        last_pos = canvas_pos

                    elif current_tool == "eraser" and last_pos is not None:
                        pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, brush_size)
                        last_pos = canvas_pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if is_dragging and start_pos is not None and inside_canvas(event.pos):
                    end_pos = to_canvas_pos(event.pos)
                    shape_tools = {
                        "line",
                        "rect",
                        "circle",
                        "square",
                        "right_triangle",
                        "equilateral_triangle",
                        "rhombus",
                    }
                    if current_tool in shape_tools:
                        draw_shape(canvas, current_tool, start_pos, end_pos, current_color, brush_size)

                is_dragging = False
                start_pos = None
                last_pos = None

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
