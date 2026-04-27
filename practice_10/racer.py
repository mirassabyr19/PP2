import pygame
import random

pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)

# Player
player = pygame.Rect(180, 500, 40, 60)

# Enemy
enemy = pygame.Rect(random.randint(0, 360), 0, 40, 60)

# Coin
coin = pygame.Rect(random.randint(0, 370), -100, 20, 20)

speed = 5
score = 0

font = pygame.font.SysFont(None, 30)

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= 5
    if keys[pygame.K_RIGHT] and player.x < WIDTH - 40:
        player.x += 5

    # Enemy movement
    enemy.y += speed
    if enemy.y > HEIGHT:
        enemy.y = 0
        enemy.x = random.randint(0, 360)

    # Coin movement
    coin.y += speed
    if coin.y > HEIGHT:
        coin.y = 0
        coin.x = random.randint(0, 370)

    # Collision with coin
    if player.colliderect(coin):
        score += 1
        coin.y = 0
        coin.x = random.randint(0, 370)

    # Collision with enemy
    if player.colliderect(enemy):
        print("GAME OVER")
        running = False

    # Draw objects
    pygame.draw.rect(screen, RED, player)
    pygame.draw.rect(screen, (0,0,0), enemy)
    pygame.draw.circle(screen, YELLOW, (coin.x, coin.y), 10)

    # Score text (TOP RIGHT)
    text = font.render(f"Coins: {score}", True, (0,0,0))
    screen.blit(text, (WIDTH - 120, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()