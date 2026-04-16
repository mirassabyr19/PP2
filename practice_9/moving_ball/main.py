import pygame
from ball import Ball


def run_game():
    pygame.init()

    WIDTH = 800
    HEIGHT = 600

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")

    clock = pygame.time.Clock()

    # Create ball in center
    ball = Ball(WIDTH // 2, HEIGHT // 2, 25, WIDTH, HEIGHT)

    running = True
    while running:
        screen.fill((255, 255, 255))  # white background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move_up()

                elif event.key == pygame.K_DOWN:
                    ball.move_down()

                elif event.key == pygame.K_LEFT:
                    ball.move_left()

                elif event.key == pygame.K_RIGHT:
                    ball.move_right()

        # Draw ball
        ball.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


run_game()