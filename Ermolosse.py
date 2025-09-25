import pygame
import random
import os
import matplotlib.pyplot as plt

pygame.init()
screen = pygame.display.set_mode((500, 600))
clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

font = pygame.font.SysFont("Arial", 30)

# Sons
pygame.mixer.init()
sound_pass = pygame.mixer.Sound("sfx_point.mp3")
sound_die = pygame.mixer.Sound("sfx_die.mp3")

# Musique
music_on = False
pygame.mixer.music.load("nyan_cat.mp3")

# Images
bg_img = pygame.image.load("background.png").convert()
bg_img = pygame.transform.scale(bg_img, (500, 600))
bird_img = pygame.image.load("bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (34, 34))

# Fichiers et dossiers
SCORES_FILE = "scores.txt"
GRAPH_DIR = "graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

# ---- Gestion des scores et graph ----
current_cycle_scores = []

def show_graph(scores, title="Évolution des scores"):
    if not scores:
        return
    plt.figure(figsize=(5, 3))
    plt.plot(range(1, len(scores)+1), scores, marker='o', color='magenta')
    plt.title(title)
    plt.xlabel("Partie")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.show()

def save_score(score):
    global current_cycle_scores
    current_cycle_scores.append(score)

    if len(current_cycle_scores) == 10:
        # Graph automatique toutes les 10 parties
        show_graph(current_cycle_scores, "Évolution des 10 derniers scores")
        current_cycle_scores = []

    # Sauvegarder le top 10 global
    top_scores = load_top_scores_file()
    top_scores.append(score)
    top_scores = sorted(top_scores, reverse=True)[:10]
    with open(SCORES_FILE, "w") as f:
        for s in top_scores:
            f.write(str(s)+"\n")

def load_top_scores_file():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

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
        screen.blit(bird_img, self.rect.topleft)

class Pipe:
    def __init__(self, x):
        self.gap = 160
        self.width = 80
        self.x = x
        self.top_height = random.randint(100, 350)
        self.bottom_height = 600 - self.top_height - self.gap
        self.speed = 3
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        green_light = (80, 200, 120)
        green_dark = (40, 150, 80)
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(screen, green_light, top_rect)
        pygame.draw.rect(screen, green_dark, (self.x-5, self.top_height-20, self.width+10, 20))
        bottom_rect = pygame.Rect(self.x, 600-self.bottom_height, self.width, self.bottom_height)
        pygame.draw.rect(screen, green_light, bottom_rect)
        pygame.draw.rect(screen, green_dark, (self.x-5, 600-self.bottom_height, self.width+10, 20))

    def get_gap_center(self):
        return self.top_height + self.gap//2

    def collides_with(self, bird):
        return bird.rect.colliderect(pygame.Rect(self.x, 0, self.width, self.top_height)) \
               or bird.rect.colliderect(pygame.Rect(self.x, 600-self.bottom_height, self.width, self.bottom_height))

# ---- Fonctions ----
def restart_game():
    global bird, pipes, score, game_over
    bird = Bird()
    pipes = [Pipe(500)]
    score = 0
    game_over = False

def go_to_selection():
    global mode, game_over, show_scores
    mode = None
    game_over = False
    show_scores = False
    pygame.mixer.music.stop()

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect, border_radius=8)
    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x+10, rect.y+10))

# ---- Variables ----
bird = Bird()
pipes = [Pipe(500)]
score = 0
game_over = False
mode = None
sound_on = True

restart_rect = pygame.Rect(200, 400, 120, 50)
assist_rect = pygame.Rect(150, 200, 200, 50)
manual_rect = pygame.Rect(150, 270, 200, 50)
scores_rect = pygame.Rect(150, 340, 200, 50)
graph_rect = pygame.Rect(150, 410, 200, 50)  # Nouveau bouton "Graph"
sound_rect = pygame.Rect(150, 500, 200, 50)
music_rect = pygame.Rect(150, 550, 200, 50)
back_rect = pygame.Rect(180, 500, 140, 50)

show_scores = False

# ---- Boucle principale ----
running = True
while running:
    screen.blit(bg_img, (0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode is None:
                if not show_scores:
                    if assist_rect.collidepoint(event.pos):
                        mode = "assist"
                        restart_game()
                        if music_on:
                            pygame.mixer.music.play(-1)
                    elif manual_rect.collidepoint(event.pos):
                        mode = "manual"
                        restart_game()
                        if music_on:
                            pygame.mixer.music.play(-1)
                    elif scores_rect.collidepoint(event.pos):
                        show_scores = True
                    elif graph_rect.collidepoint(event.pos):
                        show_graph(current_cycle_scores, "Évolution en cours (cycle non fini)")
                    elif sound_rect.collidepoint(event.pos):
                        sound_on = not sound_on
                    elif music_rect.collidepoint(event.pos):
                        music_on = not music_on
                else:
                    if back_rect.collidepoint(event.pos):
                        show_scores = False
            elif game_over and restart_rect.collidepoint(event.pos):
                go_to_selection()
        elif event.type == pygame.KEYDOWN:
            if mode=="manual" and not game_over:
                if event.key == pygame.K_SPACE:
                    bird.flap()
            elif mode=="assist" and not game_over:
                if event.key == pygame.K_SPACE:
                    # Quitter l'IA, enregistrer le score et revenir au menu
                    game_over = True
                    save_score(score)
                    go_to_selection()

    if mode is None:
        if show_scores:
            title = font.render("Top Scores", True, BLACK)
            screen.blit(title, (160,100))
            top_scores = load_top_scores_file()
            for i,s in enumerate(top_scores):
                line = font.render(f"{i+1}. {s}", True, BLACK)
                screen.blit(line, (200,150+i*30))
            draw_button(back_rect, "Retour")
        else:
            title = font.render("Choisir le mode", True, BLACK)
            screen.blit(title, (150,100))
            draw_button(assist_rect, "Assist (IA)")
            draw_button(manual_rect, "Manuel (ESPACE)")
            draw_button(scores_rect, "Scores")
            draw_button(graph_rect, "Graph")
            draw_button(sound_rect, f"Son: {'ON' if sound_on else 'OFF'}")
            draw_button(music_rect, f"Music: {'ON' if music_on else 'OFF'}")
    else:
        if not game_over:
            bird.update()
            next_pipe = pipes[0]
            if mode=="assist" and bird.rect.y>next_pipe.get_gap_center():
                bird.flap()
            if bird.rect.top<=0 or bird.rect.bottom>=600:
                game_over=True
                if sound_on: sound_die.play()
                save_score(score)
            for pipe in pipes:
                pipe.update()
                pipe.draw(screen)
                if pipe.collides_with(bird):
                    game_over=True
                    if sound_on: sound_die.play()
                    save_score(score)
                if not pipe.passed and pipe.x+pipe.width<bird.rect.x:
                    pipe.passed=True
                    score+=1
                    if sound_on: sound_pass.play()
            if pipes[-1].x<250: pipes.append(Pipe(500))
            if pipes[0].x+pipes[0].width<0: pipes.pop(0)
        bird.draw(screen)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10,10))
        if game_over:
            over_text = font.render("GAME OVER", True, BLACK)
            screen.blit(over_text, (170,250))
            pygame.draw.rect(screen, GRAY, restart_rect, border_radius=8)
            restart_text = font.render("Restart", True, BLACK)
            screen.blit(restart_text, (restart_rect.x+15, restart_rect.y+10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()









