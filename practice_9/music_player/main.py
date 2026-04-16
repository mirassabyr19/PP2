import pygame
from player import MusicPlayer


def run_player():
    pygame.init()

    WIDTH = 800
    HEIGHT = 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")

    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 36, bold=True)
    text_font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 24)

    player = MusicPlayer()

    running = True
    while running:
        screen.fill((30, 30, 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()

                elif event.key == pygame.K_s:
                    player.stop()

                elif event.key == pygame.K_n:
                    player.next_track()

                elif event.key == pygame.K_b:
                    player.previous_track()

                elif event.key == pygame.K_q:
                    running = False

        # Title
        title_text = title_font.render("Music Player", True, (255, 255, 255))
        screen.blit(title_text, (300, 40))

        # Controls
        controls_text = small_font.render(
            "P = Play   S = Stop   N = Next   B = Previous   Q = Quit",
            True,
            (200, 200, 200)
        )
        screen.blit(controls_text, (110, 100))

        # Current track
        current_track = player.get_current_track_name()
        track_text = text_font.render(f"Current track: {current_track}", True, (255, 255, 0))
        screen.blit(track_text, (120, 180))

        # Track number
        if len(player.playlist) > 0:
            number_text = text_font.render(
                f"Track {player.current_index + 1} of {len(player.playlist)}",
                True,
                (180, 255, 180)
            )
        else:
            number_text = text_font.render("Track 0 of 0", True, (180, 255, 180))

        screen.blit(number_text, (120, 230))

        # Status
        status = "Playing" if player.is_playing else "Stopped"
        status_text = text_font.render(f"Status: {status}", True, (255, 180, 180))
        screen.blit(status_text, (120, 280))

        # Progress
        progress_seconds = player.get_progress_seconds()
        progress_text = text_font.render(f"Position: {progress_seconds} sec", True, (180, 220, 255))
        screen.blit(progress_text, (120, 330))

        # Simple progress bar
        bar_x = 120
        bar_y = 390
        bar_width = 500
        bar_height = 20

        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

        filled_width = min(progress_seconds * 10, bar_width)
        pygame.draw.rect(screen, (100, 200, 255), (bar_x, bar_y, filled_width, bar_height))

        pygame.display.update()
        clock.tick(30)

    pygame.quit()


run_player()