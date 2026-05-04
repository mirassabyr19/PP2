import pygame
import random
from db import get_personal_best

WIDTH, HEIGHT = 600, 600
CELL = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (120, 0, 0)
BLUE = (40, 120, 255)
PURPLE = (150, 60, 220)
YELLOW = (240, 220, 40)
GRAY = (100, 100, 100)
GRID = (35, 35, 35)


FOOD_TYPES = [
    {"name": "normal", "points": 1, "color": RED, "weight": 70},
    {"name": "silver", "points": 2, "color": (190, 190, 190), "weight": 25},
    {"name": "gold", "points": 3, "color": YELLOW, "weight": 5},
]

POWER_TYPES = ["speed", "slow", "shield"]


def weighted_food_type():
    """Choose food type using weights."""
    total = sum(item["weight"] for item in FOOD_TYPES)
    roll = random.randint(1, total)
    current = 0
    for item in FOOD_TYPES:
        current += item["weight"]
        if roll <= current:
            return item
    return FOOD_TYPES[0]


def random_cell(blocked):
    """Generate cell that is not occupied by snake, food, power-up, or obstacle."""
    while True:
        pos = (
            random.randrange(0, WIDTH, CELL),
            random.randrange(0, HEIGHT, CELL)
        )
        if pos not in blocked:
            return pos


def draw_grid(screen):
    """Draw optional grid overlay."""
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def create_obstacles(level, snake, food_pos=None):
    """Create static obstacles starting from level 3 without trapping the snake."""
    if level < 3:
        return []

    blocked = set(snake)
    if food_pos:
        blocked.add(food_pos)

    count = min(4 + level, 18)
    obstacles = []

    # Keep cells around the snake head free so the snake is not trapped.
    head_x, head_y = snake[0]
    safe_around_head = {
        (head_x, head_y),
        (head_x + CELL, head_y),
        (head_x - CELL, head_y),
        (head_x, head_y + CELL),
        (head_x, head_y - CELL),
    }

    attempts = 0
    while len(obstacles) < count and attempts < 500:
        attempts += 1
        pos = random_cell(blocked | set(obstacles) | safe_around_head)
        obstacles.append(pos)

    return obstacles


def run_game(screen, clock, username, settings):
    """Main Snake game loop. Returns score, level, personal_best."""
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 40)

    snake_color = tuple(settings["snake_color"])
    grid_enabled = settings["grid"]

    snake = [(100, 100), (80, 100), (60, 100)]
    dx, dy = CELL, 0
    pending_dx, pending_dy = dx, dy

    score = 0
    level = 1
    base_speed = 7
    personal_best = get_personal_best(username)

    food_type = weighted_food_type()
    food = random_cell(set(snake))
    food_spawn_time = pygame.time.get_ticks()

    poison = random_cell(set(snake) | {food})
    poison_spawn_time = pygame.time.get_ticks()

    powerup = None
    powerup_type = None
    powerup_spawn_time = 0

    active_power = None
    active_power_start = 0
    shield = False

    obstacles = []
    last_level_for_obstacles = level

    running = True
    game_over = False

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, level, personal_best, True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dy != CELL:
                    pending_dx, pending_dy = 0, -CELL
                elif event.key == pygame.K_DOWN and dy != -CELL:
                    pending_dx, pending_dy = 0, CELL
                elif event.key == pygame.K_LEFT and dx != CELL:
                    pending_dx, pending_dy = -CELL, 0
                elif event.key == pygame.K_RIGHT and dx != -CELL:
                    pending_dx, pending_dy = CELL, 0

        dx, dy = pending_dx, pending_dy
        head = (snake[0][0] + dx, snake[0][1] + dy)

        # Timed power-up effects.
        speed_modifier = 0
        if active_power in ("speed", "slow") and now - active_power_start <= 5000:
            speed_modifier = 5 if active_power == "speed" else -3
        elif active_power in ("speed", "slow") and now - active_power_start > 5000:
            active_power = None

        current_speed = max(4, base_speed + (level - 1) * 2 + speed_modifier)

        # Collision check.
        hit_wall = head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT
        hit_self = head in snake
        hit_obstacle = head in obstacles

        if hit_wall or hit_self or hit_obstacle:
            if shield:
                shield = False
                active_power = None
                # Instead of dying, reverse this movement by keeping previous snake.
                head = snake[0]
            else:
                game_over = True

        if game_over:
            running = False
            continue

        snake.insert(0, head)

        # Normal weighted food.
        if head == food:
            score += food_type["points"]
            if score // 4 + 1 > level:
                level = score // 4 + 1

            food_type = weighted_food_type()
            food = random_cell(set(snake) | set(obstacles) | {poison})
            food_spawn_time = now
        else:
            snake.pop()

        # Food disappears after timer.
        if now - food_spawn_time > 8000:
            food_type = weighted_food_type()
            food = random_cell(set(snake) | set(obstacles) | {poison})
            food_spawn_time = now

        # Poison food.
        if head == poison:
            if len(snake) > 2:
                snake = snake[:-2]
            else:
                game_over = True
            poison = random_cell(set(snake) | set(obstacles) | {food})
            poison_spawn_time = now

        if now - poison_spawn_time > 10000:
            poison = random_cell(set(snake) | set(obstacles) | {food})
            poison_spawn_time = now

        # Obstacles update at new level from level 3.
        if level >= 3 and level != last_level_for_obstacles:
            obstacles = create_obstacles(level, snake, food)
            last_level_for_obstacles = level

        if level >= 3 and not obstacles:
            obstacles = create_obstacles(level, snake, food)

        # Spawn only one field power-up at a time.
        if powerup is None and random.random() < 0.03:
            powerup_type = random.choice(POWER_TYPES)
            powerup = random_cell(set(snake) | set(obstacles) | {food, poison})
            powerup_spawn_time = now

        if powerup and now - powerup_spawn_time > 8000:
            powerup = None
            powerup_type = None

        if powerup and head == powerup:
            if powerup_type == "shield":
                shield = True
                active_power = "shield"
            else:
                active_power = powerup_type
                active_power_start = now

            powerup = None
            powerup_type = None

        # Drawing.
        screen.fill(BLACK)

        if grid_enabled:
            draw_grid(screen)

        for obs in obstacles:
            pygame.draw.rect(screen, GRAY, (*obs, CELL, CELL))

        for block in snake:
            pygame.draw.rect(screen, snake_color, (*block, CELL, CELL), border_radius=4)

        pygame.draw.rect(screen, food_type["color"], (*food, CELL, CELL), border_radius=6)
        pygame.draw.rect(screen, DARK_RED, (*poison, CELL, CELL), border_radius=6)

        if powerup:
            color = BLUE if powerup_type == "speed" else PURPLE if powerup_type == "slow" else YELLOW
            pygame.draw.rect(screen, color, (*powerup, CELL, CELL), border_radius=8)

        # UI information.
        info = f"Player: {username}   Score: {score}   Level: {level}   Best: {personal_best}"
        screen.blit(font.render(info, True, WHITE), (10, 10))

        if active_power:
            if active_power in ("speed", "slow"):
                remaining = max(0, 5 - (now - active_power_start) // 1000)
                power_text = f"Power: {active_power} ({remaining}s)"
            else:
                power_text = "Power: shield"
            screen.blit(font.render(power_text, True, YELLOW), (10, 38))

        if score > personal_best:
            screen.blit(big_font.render("New personal best!", True, YELLOW), (160, 560))

        pygame.display.update()
        clock.tick(current_speed)

    return score, level, personal_best, False
