import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

snake = [(100,100)]
dx, dy = 20, 0

food = (200,200)

score = 0
level = 1
speed = 5

def generate_food():
    while True:
        f = (random.randrange(0, WIDTH, 20),
             random.randrange(0, HEIGHT, 20))
        if f not in snake:
            return f

running = True
while running:
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                dx, dy = 0, -20
            if event.key == pygame.K_DOWN:
                dx, dy = 0, 20
            if event.key == pygame.K_LEFT:
                dx, dy = -20, 0
            if event.key == pygame.K_RIGHT:
                dx, dy = 20, 0

    # Move snake
    head = (snake[0][0] + dx, snake[0][1] + dy)

    # WALL COLLISION
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        print("GAME OVER")
        running = False

    snake.insert(0, head)

    # Eat food
    if head == food:
        score += 1
        food = generate_food()

        # LEVEL SYSTEM
        if score % 3 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    # Draw snake
    for block in snake:
        pygame.draw.rect(screen, (0,255,0), (*block, 20, 20))

    # Draw food
    pygame.draw.rect(screen, (255,0,0), (*food, 20, 20))

    # TEXT
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Score: {score} Level: {level}", True, (255,255,255))
    screen.blit(text, (10,10))

    pygame.display.update()
    clock.tick(speed)

pygame.quit()