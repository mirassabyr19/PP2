import pygame
import sys
from db import init_db, save_result, get_top_scores
from settings import load_settings, save_settings
from ui import Button, draw_text
from game import run_game, WIDTH, HEIGHT

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (20, 20, 25)
GREEN = (0, 220, 100)
RED = (220, 50, 50)
YELLOW = (240, 220, 60)

font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 54)


def username_screen():
    """Ask player to enter username using keyboard."""
    username = ""

    while True:
        screen.fill(BG)
        draw_text(screen, "Enter username", big_font, WHITE, WIDTH // 2, 160, center=True)
        draw_text(screen, "Press ENTER to continue", small_font, WHITE, WIDTH // 2, 230, center=True)

        box = pygame.Rect(150, 280, 300, 50)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=8)
        draw_text(screen, username or "type here...", font, WHITE, 165, 295)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()[:50]
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 50 and event.unicode.isprintable():
                    username += event.unicode

        pygame.display.update()
        clock.tick(60)


def main_menu(username, settings):
    """Main menu screen."""
    buttons = [
        Button(200, 190, 200, 45, "Play", font),
        Button(200, 250, 200, 45, "Leaderboard", font),
        Button(200, 310, 200, 45, "Settings", font),
        Button(200, 370, 200, 45, "Quit", font),
    ]

    while True:
        screen.fill(BG)
        draw_text(screen, "TSIS4 Snake", big_font, GREEN, WIDTH // 2, 90, center=True)
        draw_text(screen, f"Player: {username}", font, WHITE, WIDTH // 2, 135, center=True)

        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if buttons[0].clicked(event):
                return "play"
            if buttons[1].clicked(event):
                return "leaderboard"
            if buttons[2].clicked(event):
                return "settings"
            if buttons[3].clicked(event):
                return "quit"

        pygame.display.update()
        clock.tick(60)


def leaderboard_screen():
    """Show top 10 results from PostgreSQL."""
    back = Button(210, 530, 180, 45, "Back", font)

    while True:
        screen.fill(BG)
        draw_text(screen, "Leaderboard TOP 10", big_font, YELLOW, WIDTH // 2, 60, center=True)

        try:
            rows = get_top_scores()
            y = 120
            draw_text(screen, "Rank   Username        Score   Level   Date", small_font, WHITE, 55, y)
            y += 35

            for i, row in enumerate(rows, start=1):
                username, score, level, date = row
                line = f"{i:<6} {username[:12]:<14} {score:<7} {level:<7} {date}"
                draw_text(screen, line, small_font, WHITE, 55, y)
                y += 30

            if not rows:
                draw_text(screen, "No scores yet.", font, WHITE, WIDTH // 2, 250, center=True)

        except Exception as error:
            draw_text(screen, "Database error. Check PostgreSQL/config.py", small_font, RED, WIDTH // 2, 220, center=True)
            draw_text(screen, str(error)[:70], small_font, RED, WIDTH // 2, 255, center=True)

        back.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back.clicked(event):
                return "back"

        pygame.display.update()
        clock.tick(60)


def settings_screen(settings):
    """Settings screen: grid, sound, snake color."""
    colors = [
        ([0, 255, 0], "Green"),
        ([0, 160, 255], "Blue"),
        ([255, 220, 0], "Yellow"),
        ([255, 80, 180], "Pink"),
    ]

    grid_button = Button(180, 170, 240, 45, "", font)
    sound_button = Button(180, 230, 240, 45, "", font)
    color_buttons = [
        Button(180, 310 + i * 55, 240, 45, name, font)
        for i, (_, name) in enumerate(colors)
    ]
    back = Button(180, 530, 240, 45, "Save & Back", font)

    while True:
        screen.fill(BG)
        draw_text(screen, "Settings", big_font, WHITE, WIDTH // 2, 80, center=True)

        grid_button.text = f"Grid: {'ON' if settings['grid'] else 'OFF'}"
        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"

        grid_button.draw(screen)
        sound_button.draw(screen)

        draw_text(screen, "Snake color:", font, WHITE, WIDTH // 2, 285, center=True)
        for button in color_buttons:
            button.draw(screen)

        back.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if grid_button.clicked(event):
                settings["grid"] = not settings["grid"]
            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]

            for i, button in enumerate(color_buttons):
                if button.clicked(event):
                    settings["snake_color"] = colors[i][0]

            if back.clicked(event):
                save_settings(settings)
                return "back"

        pygame.display.update()
        clock.tick(60)


def game_over_screen(username, score, level, personal_best, settings):
    """Game over screen and save result to database."""
    try:
        save_result(username, score, level)
        saved_text = "Result saved to database"
    except Exception as error:
        saved_text = "DB save failed. Check PostgreSQL/config.py"

    retry = Button(180, 360, 240, 45, "Retry", font)
    menu = Button(180, 420, 240, 45, "Main Menu", font)

    while True:
        screen.fill(BG)
        draw_text(screen, "GAME OVER", big_font, RED, WIDTH // 2, 90, center=True)
        draw_text(screen, f"Score: {score}", font, WHITE, WIDTH // 2, 180, center=True)
        draw_text(screen, f"Level reached: {level}", font, WHITE, WIDTH // 2, 220, center=True)
        draw_text(screen, f"Personal best before run: {personal_best}", font, WHITE, WIDTH // 2, 260, center=True)
        draw_text(screen, saved_text, small_font, YELLOW, WIDTH // 2, 310, center=True)

        retry.draw(screen)
        menu.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"

        pygame.display.update()
        clock.tick(60)


def main():
    """Program entry point."""
    try:
        init_db()
    except Exception:
        # The game still opens, but DB screens/saving will show an error.
        pass

    settings = load_settings()
    username = username_screen()

    while True:
        choice = main_menu(username, settings)

        if choice == "quit":
            break

        if choice == "leaderboard":
            result = leaderboard_screen()
            if result == "quit":
                break

        if choice == "settings":
            result = settings_screen(settings)
            if result == "quit":
                break

        if choice == "play":
            score, level, personal_best, quit_now = run_game(screen, clock, username, settings)
            if quit_now:
                break

            while True:
                result = game_over_screen(username, score, level, personal_best, settings)
                if result == "quit":
                    pygame.quit()
                    sys.exit()
                if result == "menu":
                    break
                if result == "retry":
                    score, level, personal_best, quit_now = run_game(screen, clock, username, settings)
                    if quit_now:
                        pygame.quit()
                        sys.exit()

    pygame.quit()


if __name__ == "__main__":
    main()
