# TSIS 2: Paint Application — Extended Drawing Tools

## Objective

This project extends the Practice 10 Paint application with freehand drawing, live preview line/shape tools, adjustable brush size, flood fill, timestamped saving, and text placement.

## Project Structure

```text
TSIS2/
├── paint.py
├── tools.py
├── requirements.txt
├── README.md
├── assets/
└── saves/
```

## Completed Requirements

- Pencil freehand tool using continuous drawing between mouse positions.
- Straight line tool with live preview.
- Three brush size levels: 2 px, 5 px, 10 px.
- Brush size can be changed using toolbar buttons or keyboard shortcuts `1`, `2`, `3`.
- Flood-fill tool using `pygame.Surface.get_at()` and `pygame.Surface.set_at()`.
- `Ctrl+S` saves the current canvas as a timestamped `.png` file.
- Text tool: click on canvas, type text, press `Enter` to confirm or `Escape` to cancel.
- Practice 10 tools: rectangle, circle, eraser, color picker.
- Practice 11 tools: square, right triangle, equilateral triangle, rhombus.
- All drawing tools respect the active brush size.

## Controls

| Key | Action |
|---|---|
| `P` | Pencil |
| `L` | Straight line |
| `R` | Rectangle |
| `C` | Circle |
| `E` | Eraser |
| `F` | Flood fill |
| `T` | Text tool |
| `I` | Color picker |
| `Q` | Square |
| `Y` | Right triangle |
| `U` | Equilateral triangle |
| `H` | Rhombus |
| `1` | Small brush, 2 px |
| `2` | Medium brush, 5 px |
| `3` | Large brush, 10 px |
| `Ctrl+S` | Save canvas |

## How to Run

Install Pygame:

```bash
pip install pygame
```

Run the application:

```bash
python paint.py
```

Saved images will appear in the `saves/` folder.

## Defense Explanation

The program uses a main Pygame loop. Each frame handles events, draws the canvas, draws the toolbar, shows live previews, and updates the display.

The pencil tool draws continuously by connecting the previous mouse position to the current mouse position with `pygame.draw.line()`. This makes the line smooth and avoids gaps.

The straight line and shape tools use two points: the start point from mouse down and the end point from mouse up. While dragging, the shape is drawn temporarily on the screen as a live preview. On mouse release, it is drawn permanently onto the canvas surface.

The brush size is stored in the `brush_size` variable. It is passed into all drawing functions as the `width` parameter, so all shapes respect the active brush thickness.

The flood-fill algorithm starts from the clicked pixel, reads its color using `get_at()`, and then changes connected pixels of the same color using `set_at()`. It stops when it reaches pixels of a different color.

The text tool stores typed characters in a string. The text is shown in real time with a cursor. When the user presses `Enter`, it is rendered permanently onto the canvas.

`Ctrl+S` saves only the canvas surface, not the toolbar. The file name includes a timestamp, so old saves are not overwritten.

## Suggested Git Commands

```bash
git init
git add .
git commit -m "Initial TSIS2 paint application"
git commit -m "Add drawing tools and brush sizes"
git commit -m "Add flood fill, text tool, and canvas saving"
```
