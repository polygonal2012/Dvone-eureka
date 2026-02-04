import pygame
import random
import sys
import os

pygame.init()

# ---- Window ----
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Learning Edition")
clock = pygame.time.Clock()

# ---- Game constants ----
GRAVITY = 0.5
FLAP_STRENGTH = -9
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_VELOCITY = -4
SPAWN_INTERVAL_FRAMES = 90

# ---- Colors ----
SKY = (135, 206, 235)
GROUND = (222, 184, 135)
BIRD_COLOR = (255, 215, 0)
PIPE_COLOR = (34, 139, 34)
TEXT_COLOR = (0, 0, 0)

# ---- High score file ----
HS_PATH = os.path.join(os.path.dirname(__file__), "highscore.txt")

def load_highscore():
    try:
        with open(HS_PATH, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HS_PATH, "w") as f:
            f.write(str(int(value)))
    except Exception:
        pass

# ---- Bird class ----
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 34
        self.h = 24
        self.vel = 0

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surf):
        pygame.draw.rect(surf, BIRD_COLOR, self.rect())

# ---- Pipe class ----
class Pipe:
    def __init__(self, x):
        self.x = x
        max_top = SCREEN_HEIGHT - PIPE_GAP - 100
        self.gap_start = random.randint(60, max_top)
        self.passed = False

    def update(self):
        self.x += PIPE_VELOCITY

    def top_rect(self):
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, self.gap_start)

    def bottom_rect(self):
        return pygame.Rect(int(self.x), self.gap_start + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - (self.gap_start + PIPE_GAP))

    def draw(self, surf):
        pygame.draw.rect(surf, PIPE_COLOR, self.top_rect())
        pygame.draw.rect(surf, PIPE_COLOR, self.bottom_rect())

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0

# ---- Helper functions ----
def check_collision(bird, pipes):
    br = bird.rect()
    # off top/bottom
    if br.top <= 0 or br.bottom >= SCREEN_HEIGHT:
        return True
    for p in pipes:
        if br.colliderect(p.top_rect()) or br.colliderect(p.bottom_rect()):
            return True
    return False

def draw_text(surf, text, size, pos):
    font = pygame.font.Font(None, size)
    img = font.render(text, True, TEXT_COLOR)
    surf.blit(img, pos)

# ---- Main game ----
def main():
    bird = Bird(80, SCREEN_HEIGHT // 2)
    pipes = []
    frames = 0
    score = 0
    highscore = load_highscore()
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        frames += 1

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # restart
                        bird = Bird(80, SCREEN_HEIGHT // 2)
                        pipes = []
                        frames = 0
                        score = 0
                        game_over = False
                    else:
                        bird.flap()

        if not game_over:
            # ---- Update game objects ----
            bird.update()

            if frames % SPAWN_INTERVAL_FRAMES == 0:
                pipes.append(Pipe(SCREEN_WIDTH + 10))

            for p in pipes:
                p.update()
                # scoring: when pipe passes bird
                if not p.passed and p.x + PIPE_WIDTH < bird.x:
                    p.passed = True
                    score += 1

            # remove off-screen pipes
            pipes = [p for p in pipes if not p.off_screen()]

            # ---- Collision check ----
            if check_collision(bird, pipes):
                game_over = True
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)

        # ---- Draw ----
        screen.fill(SKY)
        # ground strip
        pygame.draw.rect(screen, GROUND, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))

        for p in pipes:
            p.draw(screen)

        bird.draw(screen)

        draw_text(screen, f"Score: {score}", 36, (10, 10))
        draw_text(screen, f"High: {highscore}", 28, (10, 50))

        if game_over:
            draw_text(screen, "GAME OVER", 56, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60))
            draw_text(screen, "Press SPACE to restart", 30, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    