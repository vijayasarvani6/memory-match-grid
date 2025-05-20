import pygame
import random
import sys

# Game settings
GRID_SIZE = 6  # 6x6 grid for more numbers
CARD_SIZE = 80
GAP = 12
WINDOW_SIZE = GRID_SIZE * CARD_SIZE + (GRID_SIZE + 1) * GAP
FPS = 30

# Colors
BG_COLOR = (0, 128, 128)  # Teal background
CARD_COLOR = (200, 200, 255)
CARD_BACK = (100, 100, 180)
TEXT_COLOR = (30, 30, 60)
MATCH_COLOR = (100, 255, 100)

# Initialize pygame and mixer for sound
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound

# Use pygame's built-in sound (a simple beep sound) when a card is flipped
flip_sound = pygame.mixer.Sound(pygame.mixer.Sound("beep-07.wav"))

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Memory Match Game")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

def generate_board(size):
    num_pairs = (size * size) // 2
    values = list(range(1, num_pairs + 1)) * 2
    random.shuffle(values)
    board = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(values.pop())
        board.append(row)
    return board

def draw_card(x, y, value, revealed, matched, flip_t):
    rect = pygame.Rect(
        GAP + x * (CARD_SIZE + GAP),
        GAP + y * (CARD_SIZE + GAP),
        CARD_SIZE, CARD_SIZE
    )
    
    # Bomb blast animation effect (expand then shrink)
    if flip_t > 0:
        scale_factor = 1 + 0.2 * (flip_t // 10)
        new_size = int(CARD_SIZE * scale_factor)
        new_rect = pygame.Rect(
            GAP + x * (CARD_SIZE + GAP) - (new_size - CARD_SIZE) // 2,
            GAP + y * (CARD_SIZE + GAP) - (new_size - CARD_SIZE) // 2,
            new_size, new_size
        )
    else:
        new_rect = rect

    if matched:
        pygame.draw.rect(screen, MATCH_COLOR, new_rect)
    elif revealed:
        pygame.draw.rect(screen, CARD_COLOR, new_rect)
        text = font.render(str(value), True, TEXT_COLOR)
        text_rect = text.get_rect(center=new_rect.center)
        screen.blit(text, text_rect)
    else:
        pygame.draw.rect(screen, CARD_BACK, new_rect)

    pygame.draw.rect(screen, BG_COLOR, new_rect, 4)

def main():
    board = generate_board(GRID_SIZE)
    revealed = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
    matched = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
    first = None
    second = None
    waiting = False
    wait_start = 0
    moves = 0
    flip_timer = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]  # Timer for bomb effect

    running = True
    while running:
        screen.fill(BG_COLOR)  # Change background color here

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                draw_card(x, y, board[y][x], revealed[y][x], matched[y][x], flip_timer[y][x])

        # Draw moves
        moves_text = font.render(f"Moves: {moves}", True, (255, 255, 255))
        screen.blit(moves_text, (10, WINDOW_SIZE - 50))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not waiting:
                mx, my = event.pos
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        rect = pygame.Rect(
                            GAP + x * (CARD_SIZE + GAP),
                            GAP + y * (CARD_SIZE + GAP),
                            CARD_SIZE, CARD_SIZE
                        )
                        if rect.collidepoint(mx, my) and not revealed[y][x] and not matched[y][x]:
                            if not first:
                                first = (x, y)
                                revealed[y][x] = True
                                flip_sound.play()  # Play flip sound
                                flip_timer[first[1]][first[0]] = 30  # Trigger bomb effect
                            elif not second and (x, y) != first:
                                second = (x, y)
                                revealed[y][x] = True
                                flip_sound.play()  # Play flip sound
                                flip_timer[second[1]][second[0]] = 30  # Trigger bomb effect
                                moves += 1
                                # Check for match
                                if board[y][x] == board[first[1]][first[0]]:
                                    matched[y][x] = True
                                    matched[first[1]][first[0]] = True
                                    first = None
                                    second = None
                                else:
                                    waiting = True
                                    wait_start = pygame.time.get_ticks()
                                    break

        # Handle delay for mismatched cards
        if waiting and pygame.time.get_ticks() - wait_start > 1000:
            revealed[first[1]][first[0]] = False
            revealed[second[1]][second[0]] = False
            first = None
            second = None
            waiting = False

        # Decrease bomb effect timer
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if flip_timer[y][x] > 0:
                    flip_timer[y][x] -= 1

        # Check for win
        if all(all(row) for row in matched):
            screen.fill(BG_COLOR)
            win_text = font.render("You Win!", True, (255, 255, 0))
            screen.blit(win_text, win_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2)))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
