import pygame
from ui import Button
from persistence import load_settings, save_settings, load_leaderboard
from racer import run_game, WIDTH, HEIGHT

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
BLUE = (50, 130, 255)

font = pygame.font.SysFont(None, 34)
big_font = pygame.font.SysFont(None, 56)
clock = pygame.time.Clock()


def draw_title(text):
    """Draw title text at the top of the screen."""
    title = big_font.render(text, True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 70)))


def get_username():
    """Ask player to enter username before game starts."""
    username = ""
    active = True

    while active:
        screen.fill(WHITE)
        draw_title("Enter Username")
        info = font.render("Type your name and press ENTER", True, BLACK)
        name_text = big_font.render(username + "|", True, BLUE)
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 170)))
        screen.blit(name_text, name_text.get_rect(center=(WIDTH // 2, 260)))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 12 and event.unicode.isprintable():
                    username += event.unicode


def main_menu():
    """Main menu screen."""
    buttons = [
        Button(140, 170, 200, 55, "Play"),
        Button(140, 240, 200, 55, "Leaderboard"),
        Button(140, 310, 200, 55, "Settings"),
        Button(140, 380, 200, 55, "Quit")
    ]

    while True:
        clock.tick(60)
        screen.fill(WHITE)
        draw_title("Racer Game")

        for button in buttons:
            button.draw(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if buttons[0].is_clicked(event):
                username = get_username()
                settings = load_settings()
                run_game(screen, username, settings)
            elif buttons[1].is_clicked(event):
                leaderboard_screen()
            elif buttons[2].is_clicked(event):
                settings_screen()
            elif buttons[3].is_clicked(event):
                pygame.quit()
                raise SystemExit


def leaderboard_screen():
    """Display top 10 scores from leaderboard.json."""
    back_button = Button(140, 620, 200, 50, "Back")

    while True:
        clock.tick(60)
        screen.fill(WHITE)
        draw_title("Leaderboard")

        leaderboard = load_leaderboard()
        y = 140

        if not leaderboard:
            empty = font.render("No scores yet", True, BLACK)
            screen.blit(empty, empty.get_rect(center=(WIDTH // 2, 180)))
        else:
            for index, item in enumerate(leaderboard[:10], start=1):
                line = f"{index}. {item['username']} | Score: {item['score']} | {item['distance']} m"
                text = font.render(line, True, BLACK)
                screen.blit(text, (35, y))
                y += 42

        back_button.draw(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if back_button.is_clicked(event):
                return


def settings_screen():
    """Settings screen: sound, car color, and difficulty."""
    settings = load_settings()
    sound_button = Button(110, 160, 260, 50, "")
    color_button = Button(110, 240, 260, 50, "")
    difficulty_button = Button(110, 320, 260, 50, "")
    back_button = Button(140, 620, 200, 50, "Back")

    colors = ["red", "blue", "green"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        clock.tick(60)
        screen.fill(WHITE)
        draw_title("Settings")

        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color_button.text = f"Car color: {settings['car_color']}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"

        for button in [sound_button, color_button, difficulty_button, back_button]:
            button.draw(screen)

        note = font.render("Settings are saved to settings.json", True, BLACK)
        screen.blit(note, note.get_rect(center=(WIDTH // 2, 430)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if sound_button.is_clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)
            elif color_button.is_clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)
            elif difficulty_button.is_clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)
            elif back_button.is_clicked(event):
                return


if __name__ == "__main__":
    main_menu()
