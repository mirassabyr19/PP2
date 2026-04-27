import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

base = pygame.Surface((WIDTH, HEIGHT))
base.fill((255,255,255))

color = (0,0,0)
mode = "draw"

start_pos = None

running = True
while running:
    screen.blit(base, (0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # CHANGE MODE
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                mode = "rect"
            if event.key == pygame.K_c:
                mode = "circle"
            if event.key == pygame.K_e:
                mode = "erase"
            if event.key == pygame.K_1:
                color = (255,0,0)
            if event.key == pygame.K_2:
                color = (0,255,0)
            if event.key == pygame.K_3:
                color = (0,0,255)

        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            end_pos = event.pos

            if mode == "rect":
                pygame.draw.rect(base, color,
                    (start_pos[0], start_pos[1],
                     end_pos[0]-start_pos[0],
                     end_pos[1]-start_pos[1]))

            elif mode == "circle":
                radius = int(((end_pos[0]-start_pos[0])**2 +
                              (end_pos[1]-start_pos[1])**2)**0.5)
                pygame.draw.circle(base, color, start_pos, radius)

        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if mode == "draw":
                    pygame.draw.circle(base, color, event.pos, 5)
                if mode == "erase":
                    pygame.draw.circle(base, (255,255,255), event.pos, 10)

    pygame.display.update()

pygame.quit()