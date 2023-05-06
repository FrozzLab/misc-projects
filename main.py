import sys

import pygame
import numpy

COLOR_ALIVE = (95, 110, 80)
COLOR_DEAD = (255, 255, 255)
COLOR_BACKGROUND = (140, 155, 130)
COLOR_INPUT_INACTIVE = (255, 255, 255)
COLOR_INPUT_ACTIVE = (200, 255, 255)

SIZE_X = 40
SIZE_Y = 40
CELL_SIZE = 20
FPS = 3

RULES_ALIVE_STRING = "2, 3"
RULES_DEAD_STRING = "3"

RULES_ALIVE = list(map(int, RULES_ALIVE_STRING.split(",")))
RULES_DEAD = list(map(int, RULES_DEAD_STRING.split(",")))


def display_without_updating(surface, current):
    for row, column in numpy.ndindex(current.shape):
        if current[row, column] == 1:
            color = COLOR_ALIVE
        else:
            color = COLOR_DEAD

        pygame.draw.rect(surface, color, (column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))


def count_alive(current, row, column):
    alive_count = 0

    for i in range(-1, 2):
        for j in range(-1, 2):
            if row + i < 0 and column + j < 0:
                alive_count += current[SIZE_Y - 1, SIZE_X - 1]

            elif row + i < 0 and (0 <= column + j <= SIZE_X - 1):
                alive_count += current[SIZE_Y - 1, column + j]

            elif row + i < 0 and column + j > SIZE_X - 1:
                alive_count += current[SIZE_Y - 1, 0]

            elif (0 <= row + i <= SIZE_Y - 1) and column + j < 0:
                alive_count += current[row + i, SIZE_X - 1]

            elif (0 <= row + i <= SIZE_Y - 1) and (0 <= column + j <= SIZE_X - 1):
                alive_count += current[row + i, column + j]

            elif (0 <= row + i <= SIZE_Y - 1) and column + j > SIZE_X - 1:
                alive_count += current[row + i, 0]

            elif row + i > SIZE_Y - 1 and column + j < 0:
                alive_count += current[0, SIZE_X - 1]

            elif row + i > SIZE_Y - 1 and (0 <= column + j <= SIZE_X - 1):
                alive_count += current[0, column + j]

            elif row + i > SIZE_Y - 1 and column + j > SIZE_X - 1:
                alive_count += current[0, 0]

    return alive_count - current[row, column]


def update(surface, current):
    next_iteration = numpy.zeros((current.shape[0], current.shape[1]))

    for row, column in numpy.ndindex(current.shape):
        alive_count = count_alive(current, row, column)

        if current[row, column] == 1 and alive_count not in RULES_ALIVE:
            color = COLOR_ALIVE
        elif (current[row, column] == 1 and alive_count in RULES_ALIVE) or \
                (current[row, column] == 0 and alive_count in RULES_DEAD):
            next_iteration[row, column] = 1
            color = COLOR_ALIVE

        if current[row, column] != 1:
            color = COLOR_DEAD

        pygame.draw.rect(surface, color, (column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    return next_iteration


def initialize_visuals():
    global alive_frame, alive_input_box, alive_text, clear_button, clear_text, \
        dead_frame, dead_input_box, dead_text, pause_text, \
        rules_font, start_button, start_text

    pygame.init()

    font = pygame.font.SysFont('Comic Sans', 20)
    rules_font = pygame.font.SysFont('Comic Sans', 15)

    start_text = font.render("Start", True, "White")
    pause_text = font.render("Pause", True, "White")
    clear_text = font.render("Clear field", True, "White")
    alive_text = font.render("Alive rules:", True, "White")
    dead_text = font.render("Dead rules:", True, "White")

    start_button = pygame.Rect(SIZE_X * CELL_SIZE + 50, 30, 100, 50)
    clear_button = pygame.Rect(SIZE_X * CELL_SIZE + 25, 100, 150, 50)
    alive_frame = pygame.Rect(SIZE_X * CELL_SIZE + 25, 215, 150, 90)
    dead_frame = pygame.Rect(SIZE_X * CELL_SIZE + 25, 325, 150, 90)
    alive_input_box = pygame.Rect(SIZE_X * CELL_SIZE + 35, 265, 130, 30)
    dead_input_box = pygame.Rect(SIZE_X * CELL_SIZE + 35, 375, 130, 30)

    return alive_frame, alive_input_box, alive_text, clear_button, clear_text, dead_frame, \
        dead_input_box, dead_text, pause_text, rules_font, start_button, start_text


def handle_keyboard_events(event, alive_input_active, dead_input_active):
    global RULES_ALIVE_STRING, RULES_DEAD_STRING

    if alive_input_active:
        if event.key == pygame.K_BACKSPACE:
            RULES_ALIVE_STRING = RULES_ALIVE_STRING[:-1]

        elif event.key == pygame.K_RETURN:
            alive_input_active = False

        else:
            RULES_ALIVE_STRING += event.unicode

    elif dead_input_active:
        if event.key == pygame.K_BACKSPACE:
            RULES_DEAD_STRING = RULES_DEAD_STRING[:-1]

        elif event.key == pygame.K_RETURN:
            dead_input_active = False

        else:
            RULES_DEAD_STRING += event.unicode

    return alive_input_active, dead_input_active


def handle_mouse_events(cells, is_running, alive_input_active, dead_input_active, x, y):
    if (x < SIZE_X * CELL_SIZE and y < SIZE_Y * CELL_SIZE) \
            and not is_running:
        if cells[int(y / CELL_SIZE), int(x / CELL_SIZE)] == 1:
            cells[int(y / CELL_SIZE), int(x / CELL_SIZE)] = 0
        else:
            cells[int(y / CELL_SIZE), int(x / CELL_SIZE)] = 1

    elif start_button.collidepoint(x, y):
        is_running = not is_running

    elif clear_button.collidepoint(x, y):
        cells = numpy.zeros((SIZE_Y, SIZE_X))

    elif alive_input_box.collidepoint(x, y):
        alive_input_active = not alive_input_active
        dead_input_active = False if dead_input_active else dead_input_active

    elif dead_input_box.collidepoint(x, y):
        dead_input_active = not dead_input_active
        alive_input_active = False if alive_input_active else alive_input_active

    else:
        alive_input_active = False
        dead_input_active = False

    return cells, is_running, alive_input_active, dead_input_active


def draw_paused_state(surface, cells, alive_input_active, dead_input_active):
    pygame.draw.rect(surface, (150, 130, 155), clear_button)
    pygame.draw.rect(surface, (150, 130, 155), alive_frame)
    pygame.draw.rect(surface, (150, 130, 155), dead_frame)

    if alive_input_active:
        pygame.draw.rect(surface, COLOR_INPUT_ACTIVE, alive_input_box)
    else:
        pygame.draw.rect(surface, COLOR_INPUT_INACTIVE, alive_input_box)

    if dead_input_active:
        pygame.draw.rect(surface, COLOR_INPUT_ACTIVE, dead_input_box)
    else:
        pygame.draw.rect(surface, COLOR_INPUT_INACTIVE, dead_input_box)

    surface.blit(start_text, (start_button.x + 24, start_button.y + 9))
    surface.blit(clear_text, (clear_button.x + 24, clear_button.y + 9))
    surface.blit(alive_text, (alive_frame.x + 21, alive_frame.y + 9))
    surface.blit(dead_text, (dead_frame.x + 22, dead_frame.y + 9))

    alive_rules_text = rules_font.render(RULES_ALIVE_STRING, True, "Black")
    dead_rules_text = rules_font.render(RULES_DEAD_STRING, True, "Black")

    surface.blit(alive_rules_text, (alive_frame.x + 17, alive_frame.y + 54))
    surface.blit(dead_rules_text, (dead_frame.x + 17, dead_frame.y + 54))

    display_without_updating(surface, cells)


def main():
    global RULES_ALIVE_STRING, RULES_DEAD_STRING, RULES_ALIVE, RULES_DEAD

    pygame.init()

    initialize_visuals()

    surface = pygame.display.set_mode((SIZE_X * CELL_SIZE + 200, SIZE_Y * CELL_SIZE))
    pygame.display.set_caption("Game of life")

    cells = numpy.zeros((SIZE_Y, SIZE_X))

    is_running = False
    alive_input_active = False
    dead_input_active = False

    while True:
        x, y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                cells, is_running, alive_input_active, dead_input_active = \
                    handle_mouse_events(cells, is_running, alive_input_active, dead_input_active, x, y)

            elif event.type == pygame.KEYDOWN:
                alive_input_active, dead_input_active = \
                    handle_keyboard_events(event, alive_input_active, dead_input_active)

        surface.fill(COLOR_BACKGROUND)
        pygame.draw.rect(surface, (150, 130, 155), start_button)

        if is_running:
            alive_input_active = False
            dead_input_active = False

            RULES_ALIVE = list(map(int, RULES_ALIVE_STRING.split(",")))
            RULES_DEAD = list(map(int, RULES_DEAD_STRING.split(",")))

            surface.blit(pause_text, (start_button.x + 24, start_button.y + 9))

            pygame.time.wait(int(1000 / FPS))

            cells = update(surface, cells)
        else:
            draw_paused_state(surface, cells, alive_input_active, dead_input_active)

        pygame.display.update()


if __name__ == "__main__":
    main()
