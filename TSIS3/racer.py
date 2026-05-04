import pygame
import random
import time
from persistence import add_score

WIDTH, HEIGHT = 480, 700
ROAD_LEFT = 80
ROAD_RIGHT = 400
LANE_WIDTH = 80
LANES = [100, 180, 260, 340]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK_GRAY = (45, 45, 45)
YELLOW = (255, 220, 0)
RED = (220, 50, 50)
BLUE = (50, 120, 255)
GREEN = (50, 210, 90)
ORANGE = (255, 160, 0)
PURPLE = (160, 80, 220)

COLOR_MAP = {
    "red": RED,
    "blue": BLUE,
    "green": GREEN
}

DIFFICULTY_SETTINGS = {
    "easy": {"speed": 4, "enemy_limit": 2},
    "normal": {"speed": 5, "enemy_limit": 3},
    "hard": {"speed": 7, "enemy_limit": 4}
}


class FallingObject:
    """Object that moves down the road: enemy, obstacle, coin, or power-up."""
    def __init__(self, kind, rect, color, value=0, power_type=None):
        self.kind = kind
        self.rect = rect
        self.color = color
        self.value = value
        self.power_type = power_type

    def move(self, speed):
        """Move object down."""
        self.rect.y += speed

    def draw(self, screen):
        """Draw object depending on its kind."""
        if self.kind == "coin":
            pygame.draw.circle(screen, self.color, self.rect.center, self.rect.width // 2)
        elif self.kind == "power":
            pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=5)


def random_lane_x(width):
    """Return x coordinate centered in a random lane."""
    return random.choice(LANES) - width // 2


def make_enemy(player):
    """Create enemy car with safe spawn logic."""
    while True:
        rect = pygame.Rect(random_lane_x(42), random.randint(-500, -80), 42, 62)
        if not rect.colliderect(player):
            return FallingObject("enemy", rect, BLACK)


def make_obstacle(player):
    """Create road obstacle or oil spill with safe spawn logic."""
    while True:
        obstacle_type = random.choice(["barrier", "oil", "pothole"])
        color = ORANGE if obstacle_type == "barrier" else DARK_GRAY
        rect = pygame.Rect(random_lane_x(45), random.randint(-600, -80), 45, 35)
        if not rect.colliderect(player):
            return FallingObject("obstacle", rect, color)


def make_coin(player):
    """Create weighted coin: bronze, silver, or gold."""
    choices = [
        (1, ORANGE, 60),
        (2, (190, 190, 190), 30),
        (3, YELLOW, 10)
    ]
    total_weight = sum(item[2] for item in choices)
    roll = random.randint(1, total_weight)
    current = 0

    for value, color, weight in choices:
        current += weight
        if roll <= current:
            rect = pygame.Rect(random_lane_x(22), random.randint(-700, -100), 22, 22)
            if not rect.colliderect(player):
                return FallingObject("coin", rect, color, value=value)


def make_powerup(player):
    """Create power-up: Nitro, Shield, or Repair."""
    power_type = random.choice(["nitro", "shield", "repair"])
    color = BLUE if power_type == "nitro" else GREEN if power_type == "shield" else PURPLE
    rect = pygame.Rect(random_lane_x(32), random.randint(-900, -150), 32, 32)
    if not rect.colliderect(player):
        return FallingObject("power", rect, color, power_type=power_type)
    return make_powerup(player)


def draw_road(screen, stripe_offset):
    """Draw road, lane lines, and scrolling stripes."""
    screen.fill((40, 130, 40))
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    for x in [160, 240, 320]:
        y = -70 + stripe_offset
        while y < HEIGHT:
            pygame.draw.rect(screen, WHITE, (x - 3, y, 6, 40))
            y += 80


def draw_car(screen, rect, color):
    """Draw player car."""
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, (rect.x + 8, rect.y + 10, rect.width - 16, 15), border_radius=4)
    pygame.draw.circle(screen, BLACK, (rect.x + 7, rect.y + 12), 5)
    pygame.draw.circle(screen, BLACK, (rect.right - 7, rect.y + 12), 5)
    pygame.draw.circle(screen, BLACK, (rect.x + 7, rect.bottom - 12), 5)
    pygame.draw.circle(screen, BLACK, (rect.right - 7, rect.bottom - 12), 5)


def run_game(screen, username, settings):
    """Main Racer game loop."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 54)

    difficulty = settings.get("difficulty", "normal")
    base_speed = DIFFICULTY_SETTINGS[difficulty]["speed"]
    enemy_limit = DIFFICULTY_SETTINGS[difficulty]["enemy_limit"]
    car_color = COLOR_MAP.get(settings.get("car_color", "red"), RED)

    player = pygame.Rect(220, 590, 42, 65)
    enemies = [make_enemy(player)]
    obstacles = []
    coins = [make_coin(player)]
    powerups = []

    coins_collected = 0
    score = 0
    distance = 0
    lives = 1
    shield = False
    active_power = None
    power_end_time = 0
    stripe_offset = 0
    last_event_time = time.time()

    running = True
    game_over = False

    while running:
        clock.tick(60)
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return run_game(screen, username, settings)
                if event.key == pygame.K_m:
                    return

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > ROAD_LEFT:
                player.x -= 6
            if keys[pygame.K_RIGHT] and player.right < ROAD_RIGHT:
                player.x += 6
            if keys[pygame.K_UP] and player.top > 0:
                player.y -= 4
            if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
                player.y += 4

            nitro_active = active_power == "nitro" and current_time < power_end_time
            current_speed = base_speed + int(distance // 500) + (4 if nitro_active else 0)

            distance += current_speed * 0.08
            score = int(distance) + coins_collected * 25
            stripe_offset = (stripe_offset + current_speed) % 80

            # Dynamic traffic difficulty scaling.
            if len(enemies) < enemy_limit + int(distance // 800):
                enemies.append(make_enemy(player))

            # Dynamic road events: new obstacles and power-ups appear sometimes.
            if current_time - last_event_time > 2:
                if random.random() < 0.7:
                    obstacles.append(make_obstacle(player))
                if random.random() < 0.4 and len(powerups) < 1:
                    powerups.append(make_powerup(player))
                last_event_time = current_time

            if len(coins) < 2:
                coins.append(make_coin(player))

            all_objects = enemies + obstacles + coins + powerups
            for obj in all_objects[:]:
                obj.move(current_speed)

                if obj.rect.top > HEIGHT:
                    if obj in enemies:
                        enemies.remove(obj)
                        enemies.append(make_enemy(player))
                    elif obj in obstacles:
                        obstacles.remove(obj)
                    elif obj in coins:
                        coins.remove(obj)
                        coins.append(make_coin(player))
                    elif obj in powerups:
                        powerups.remove(obj)

            for coin in coins[:]:
                if player.colliderect(coin.rect):
                    coins_collected += coin.value
                    coins.remove(coin)
                    coins.append(make_coin(player))

            for power in powerups[:]:
                if player.colliderect(power.rect):
                    if active_power is None or current_time >= power_end_time:
                        if power.power_type == "nitro":
                            active_power = "nitro"
                            power_end_time = current_time + 5
                        elif power.power_type == "shield":
                            active_power = "shield"
                            shield = True
                            power_end_time = 999999999
                        elif power.power_type == "repair":
                            lives += 1
                    powerups.remove(power)

            if active_power == "nitro" and current_time >= power_end_time:
                active_power = None

            for danger in enemies + obstacles:
                if player.colliderect(danger.rect):
                    if shield:
                        shield = False
                        active_power = None
                        if danger in enemies:
                            enemies.remove(danger)
                            enemies.append(make_enemy(player))
                        if danger in obstacles:
                            obstacles.remove(danger)
                    elif lives > 0:
                        lives -= 1
                        player.x = 220
                        player.y = 590
                    else:
                        game_over = True
                        add_score(username, score, int(distance), coins_collected)

        draw_road(screen, stripe_offset)
        draw_car(screen, player, car_color)

        for obj in enemies + obstacles + coins + powerups:
            obj.draw(screen)

        screen.blit(font.render(f"User: {username}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 35))
        screen.blit(font.render(f"Coins: {coins_collected}", True, WHITE), (10, 60))
        screen.blit(font.render(f"Distance: {int(distance)} m", True, WHITE), (10, 85))
        screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10, 110))

        if active_power == "nitro":
            remaining = max(0, int(power_end_time - current_time))
            screen.blit(font.render(f"Power-up: Nitro {remaining}s", True, BLUE), (250, 10))
        elif shield:
            screen.blit(font.render("Power-up: Shield", True, GREEN), (250, 10))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            title = big_font.render("GAME OVER", True, WHITE)
            info = font.render(f"Score: {score}  Distance: {int(distance)}  Coins: {coins_collected}", True, WHITE)
            retry = font.render("Press R to Retry or M for Main Menu", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 280)))
            screen.blit(info, info.get_rect(center=(WIDTH // 2, 340)))
            screen.blit(retry, retry.get_rect(center=(WIDTH // 2, 390)))

        pygame.display.update()
