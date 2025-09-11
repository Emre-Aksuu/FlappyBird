import pygame
import random

pygame.init()
screen = pygame.display.set_mode((400, 600))
clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

font = pygame.font.SysFont("Arial", 30)

# ---- Charger les sons ----
pygame.mixer.init()
sound_pass = pygame.mixer.Sound("sfx_point.mp3")   # son quand on passe un tuyau
sound_die = pygame.mixer.Sound("sfx_die.mp3")      # son quand on meurt
sound_enabled = True  # booléen pour activer/désactiver le son

# ---- Classes ----
class Bird:
    def __init__(self):
        self.rect = pygame.Rect(50, 300, 34, 34)
        self.velocity = 0
        self.gravity = 0.5
        self.jump = -8

    def update(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity

    def flap(self):
        self.velocity = self.jump

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)

class Pipe:
    def __init__(self, x):
        self.gap = 150
        self.width = 60
        self.x = x
        self.top_height = random.randint(100, 400)
        self.bottom_height = 600 - self.top_height - self.gap
        self.speed = 3
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, 600 - self.bottom_height, self.width, self.bottom_height))

    def get_gap_center(self):
        return self.top_height + self.gap // 2

    def collides_with(self, bird):
        return bird.rect.colliderect(pygame.Rect(self.x, 0, self.width, self.top_height)) \
               or bird.rect.colliderect(pygame.Rect(self.x, 600 - self.bottom_height, self.width, self.bottom_height))

# ---- Fonctions ----
def restart_game():
    global bird, pipes, score, game_over
    bird = Bird()
    pipes = [Pipe(400)]
    score = 0
    game_over = False

def go_to_selection():
    global mode, game_over
    mode = None
    game_over = False

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect)
    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x + 5, rect.y + 10))

# ---- Variables ----
bird = Bird()
pipes = [Pipe(400)]
score = 0
game_over = False
mode = None  # "manual" ou "assist"
sound_on = True  # son activé/désactivé

restart_rect = pygame.Rect(150, 400, 100, 50)
assist_rect = pygame.Rect(100, 200, 200, 50)
manual_rect = pygame.Rect(100, 300, 200, 50)
sound_rect = pygame.Rect(100, 500, 200, 50)  # bouton son

# ---- Boucle principale ----
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode is None:
                # choix du mode
                if assist_rect.collidepoint(event.pos):
                    mode = "assist"
                    restart_game()
                elif manual_rect.collidepoint(event.pos):
                    mode = "manual"
                    restart_game()
                elif sound_rect.collidepoint(event.pos):
                    sound_on = not sound_on
            elif game_over and restart_rect.collidepoint(event.pos):
                go_to_selection()
        elif event.type == pygame.KEYDOWN:
            if mode == "manual" and not game_over:
                if event.key == pygame.K_SPACE:
                    bird.flap()

    if mode is None:
        # Écran de sélection avec bouton son
        title = font.render("Choisir le mode", True, BLACK)
        screen.blit(title, (100, 100))
        draw_button(assist_rect, "Assist (IA)")
        draw_button(manual_rect, "Manuel (ESPACE)")
        draw_button(sound_rect, f"Son: {'ON' if sound_on else 'OFF'}")
    else:
        if not game_over:
            bird.update()
            next_pipe = pipes[0]

            # IA simple
            if mode == "assist":
                if bird.rect.y > next_pipe.get_gap_center():
                    bird.flap()

            # ---- Vérif haut et bas ----
            if bird.rect.top <= 0 or bird.rect.bottom >= 600:
                game_over = True
                if sound_on:
                    sound_die.play()

            # Mise à jour tuyaux
            for pipe in pipes:
                pipe.update()
                pipe.draw(screen)

                if pipe.collides_with(bird):
                    game_over = True
                    if sound_on:
                        sound_die.play()

                if not pipe.passed and pipe.x + pipe.width < bird.rect.x:
                    pipe.passed = True
                    score += 1
                    if sound_on:
                        sound_pass.play()

            if pipes[-1].x < 200:
                pipes.append(Pipe(400))

            if pipes[0].x + pipes[0].width < 0:
                pipes.pop(0)

        bird.draw(screen)

        # Score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Game Over + bouton Restart
        if game_over:
            over_text = font.render("GAME OVER", True, BLACK)
            screen.blit(over_text, (120, 250))
            pygame.draw.rect(screen, GRAY, restart_rect)
            restart_text = font.render("Restart", True, BLACK)
            screen.blit(restart_text, (restart_rect.x + 5, restart_rect.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()













