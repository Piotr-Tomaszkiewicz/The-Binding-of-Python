import pygame
import random
import math

# Importy z Twoich nowych plików danych
from roomdata import ROOM_TEMPLATES
from enemydata import ENEMY_TYPES
from enemyai import update_enemy_behavior, handle_death

# Inicjalizacja
pygame.init()

# --- STAŁE ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
TILE_SIZE = 40  
ROOM_DIM = 16
ROOM_WIDTH_PX = ROOM_DIM * TILE_SIZE
ROOM_HEIGHT_PX = ROOM_DIM * TILE_SIZE
ROOM_OFFSET_X = (SCREEN_WIDTH - ROOM_WIDTH_PX) // 2
ROOM_OFFSET_Y = (SCREEN_HEIGHT - ROOM_HEIGHT_PX) // 2

# Kolory
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (50, 50, 50)
GREEN, RED, YELLOW, BLUE = (100, 255, 100), (255, 50, 50), (255, 255, 0), (0, 100, 255)
LIGHT_GRAY = (160, 160, 160)
MINIMAP_BG = (30, 30, 30)

# Ustawienia ekranu
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("The Binding of Python")
clock = pygame.time.Clock()

# Czcionki
menu_font = pygame.font.SysFont('Arial', 40, bold=True)
small_font = pygame.font.SysFont('Arial', 20)

# --- KLASY ---
class Enemy:
    def __init__(self, x_grid, y_grid, enemy_id):
        data = ENEMY_TYPES[enemy_id]
        self.id = enemy_id
        self.name = data["name"]
        self.max_hp = data["hp"]
        self.hp = data["hp"]
        self.speed = data["speed"]
        self.flying = data["flying"]
        self.behavior_type = data["behavior"]
        self.color = data["color"]
        
        # Prostokąt kolizji przeciwnika
        self.rect = pygame.Rect(
            ROOM_OFFSET_X + x_grid * TILE_SIZE + 5,
            ROOM_OFFSET_Y + y_grid * TILE_SIZE + 5,
            30, 30
        )

# --- FUNKCJE POMOCNICZE ---

def draw_button(color, rect, text, font, t_color):
    """Rysuje przycisk z wyśrodkowanym tekstem."""
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (0, 80, 0), rect, 4, border_radius=12)
    text_surf = font.render(text, True, t_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def generate_map():
    """Generuje strukturę pokoi 9x9 i przypisuje im layouty oraz przeciwników."""
    temp_grid = [[0 for _ in range(9)] for _ in range(9)]
    start_pos = (4, 4)
    temp_grid[start_pos[1]][start_pos[0]] = 4 # START
    
    rooms_list = [start_pos]
    for _ in range(6):
        px, py = random.choice(rooms_list)
        dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        nx, ny = px+dx, py+dy
        if 0 <= nx < 9 and 0 <= ny < 9 and temp_grid[ny][nx] == 0:
            temp_grid[ny][nx] = 1 # Zwykły pokój
            rooms_list.append((nx, ny))
    
    # Boss i Treasure w ślepych zaułkach
    candidates = [(x,y) for y in range(9) for x in range(9) if temp_grid[y][x] == 0 and 
                  sum(1 for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)] 
                      if 0<=x+dx<9 and 0<=y+dy<9 and temp_grid[y+dy][x+dx]!=0) == 1]
    random.shuffle(candidates)
    if len(candidates) >= 2:
        temp_grid[candidates[0][1]][candidates[0][0]] = 2 # Treasure
        temp_grid[candidates[1][1]][candidates[1][0]] = 3 # Boss

    final_map = {}
    for y in range(9):
        for x in range(9):
            rtype = temp_grid[y][x]
            if rtype != 0:
                layout = [[0 for _ in range(16)] for _ in range(16)]
                enemies = []
                
                if rtype == 1: # Zwykły pokój
                    raw_layout = random.choice(ROOM_TEMPLATES)
                    for ly in range(16):
                        for lx in range(16):
                            val = raw_layout[ly][lx]
                            if val == 1: layout[ly][lx] = 1 # Kamień
                            elif isinstance(val, str) and val in ENEMY_TYPES:
                                enemies.append(Enemy(lx, ly, val))
                elif rtype == 4: # Startowy
                    layout = [[0 for _ in range(16)] for _ in range(16)]
                
                final_map[(x, y)] = {"type": rtype, "layout": layout, "enemies": enemies}
    return final_map

def check_tile_collision(rect, layout):
    """Sprawdza kolizję prostokąta z kamieniami w pokoju."""
    for y in range(16):
        for x in range(16):
            if layout[y][x] == 1:
                stone_rect = pygame.Rect(ROOM_OFFSET_X + x*TILE_SIZE, ROOM_OFFSET_Y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(stone_rect):
                    return True
    return False

def draw_room(room_data):
    """Rysuje podłogę, kamienie, drzwi i przeciwników."""
    layout = room_data["layout"]
    # Podłoga i kamienie
    for y in range(16):
        for x in range(16):
            rect = pygame.Rect(ROOM_OFFSET_X + x*TILE_SIZE, ROOM_OFFSET_Y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (45, 45, 45), rect)
            pygame.draw.rect(screen, (35, 35, 35), rect, 1)
            if layout[y][x] == 1:
                pygame.draw.rect(screen, LIGHT_GRAY, rect.inflate(-4, -4))

    # Drzwi
    rx, ry = current_room
    line_w = 10
    for dx, dy, side in [(0,-1,"top"), (0,1,"bottom"), (-1,0,"left"), (1,0,"right")]:
        if (rx+dx, ry+dy) in game_map:
            color = BLUE
            if side == "top": pygame.draw.line(screen, color, (ROOM_OFFSET_X + 7*TILE_SIZE, ROOM_OFFSET_Y), (ROOM_OFFSET_X + 9*TILE_SIZE, ROOM_OFFSET_Y), line_w)
            if side == "bottom": pygame.draw.line(screen, color, (ROOM_OFFSET_X + 7*TILE_SIZE, ROOM_OFFSET_Y + ROOM_HEIGHT_PX), (ROOM_OFFSET_X + 9*TILE_SIZE, ROOM_OFFSET_Y + ROOM_HEIGHT_PX), line_w)
            if side == "left": pygame.draw.line(screen, color, (ROOM_OFFSET_X, ROOM_OFFSET_Y + 7*TILE_SIZE), (ROOM_OFFSET_X, ROOM_OFFSET_Y + 9*TILE_SIZE), line_w)
            if side == "right": pygame.draw.line(screen, color, (ROOM_OFFSET_X + ROOM_WIDTH_PX, ROOM_OFFSET_Y + 7*TILE_SIZE), (ROOM_OFFSET_X + ROOM_WIDTH_PX, ROOM_OFFSET_Y + 9*TILE_SIZE), line_w)

    # Przeciwnicy
    for e in room_data["enemies"]:
        pygame.draw.rect(screen, e.color, e.rect)
        # Pasek HP
        if e.hp > 0:
            hp_bar_w = (e.hp / e.max_hp) * e.rect.width
            pygame.draw.rect(screen, RED, (e.rect.x, e.rect.y - 10, e.rect.width, 5))
            pygame.draw.rect(screen, GREEN, (e.rect.x, e.rect.y - 10, hp_bar_w, 5))

def draw_minimap():
    """Rysuje małą mapę w rogu ekranu."""
    ms = 12
    ox, oy = SCREEN_WIDTH - 140, 20
    pygame.draw.rect(screen, MINIMAP_BG, (ox-5, oy-5, 9*ms+10, 9*ms+10))
    for (x, y), data in game_map.items():
        color = WHITE
        if data["type"] == 2: color = YELLOW
        if data["type"] == 3: color = RED
        if data["type"] == 4: color = (150, 150, 255)
        if [x, y] == current_room: color = (0, 255, 0)
        pygame.draw.rect(screen, color, (ox + x*ms, oy + y*ms, ms-1, ms-1))

# --- ZMIENNE STANU GRY ---
scene = 0
running = True
current_seed = None
game_map = {}
current_room = [4, 4]
player_x, player_y = 0.0, 0.0
player_speed = 5.0
player_size = 30

# Przyciski menu
start_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 80, 240, 60)
quit_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 20, 240, 60)

def start_new_game():
    global scene, current_seed, game_map, current_room, player_x, player_y
    current_seed = random.randint(0, 99999999)
    random.seed(current_seed)
    game_map = generate_map()
    current_room = [4, 4]
    player_x = SCREEN_WIDTH // 2 - player_size // 2
    player_y = SCREEN_HEIGHT // 2 - player_size // 2
    scene = 1

# --- PĘTLA GŁÓWNA ---
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and scene == 0:
            if start_rect.collidepoint(event.pos): start_new_game()
            if quit_rect.collidepoint(event.pos): running = False

    if scene == 0:
        screen.fill(WHITE)
        draw_button(GREEN, start_rect, "START", menu_font, BLACK)
        draw_button(RED, quit_rect, "QUIT", menu_font, BLACK)
    
    elif scene == 1:
        # Poruszanie się (WSAD)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= player_speed
        if keys[pygame.K_s]: dy += player_speed
        if keys[pygame.K_a]: dx -= player_speed
        if keys[pygame.K_d]: dx += player_speed

        # Aktualny pokój
        room = game_map[tuple(current_room)]
        layout = room["layout"]

        # Kolizje X
        new_rect_x = pygame.Rect(player_x + dx, player_y, player_size, player_size)
        if not check_tile_collision(new_rect_x, layout):
            if ROOM_OFFSET_X <= new_rect_x.x <= ROOM_OFFSET_X + ROOM_WIDTH_PX - player_size:
                player_x += dx
            else:
                # Drzwi poziome
                rel_y = player_y - ROOM_OFFSET_Y
                if 7*TILE_SIZE < rel_y < 9*TILE_SIZE:
                    if new_rect_x.x < ROOM_OFFSET_X and (current_room[0]-1, current_room[1]) in game_map:
                        current_room[0] -= 1; player_x = ROOM_OFFSET_X + ROOM_WIDTH_PX - player_size
                    elif new_rect_x.x > ROOM_OFFSET_X + ROOM_WIDTH_PX - player_size and (current_room[0]+1, current_room[1]) in game_map:
                        current_room[0] += 1; player_x = ROOM_OFFSET_X

        # Kolizje Y
        new_rect_y = pygame.Rect(player_x, player_y + dy, player_size, player_size)
        if not check_tile_collision(new_rect_y, layout):
            if ROOM_OFFSET_Y <= new_rect_y.y <= ROOM_OFFSET_Y + ROOM_HEIGHT_PX - player_size:
                player_y += dy
            else:
                # Drzwi pionowe
                rel_x = player_x - ROOM_OFFSET_X
                if 7*TILE_SIZE < rel_x < 9*TILE_SIZE:
                    if new_rect_y.y < ROOM_OFFSET_Y and (current_room[0], current_room[1]-1) in game_map:
                        current_room[1] -= 1; player_y = ROOM_OFFSET_Y + ROOM_HEIGHT_PX - player_size
                    elif new_rect_y.y > ROOM_OFFSET_Y + ROOM_HEIGHT_PX - player_size and (current_room[0], current_room[1]+1) in game_map:
                        current_room[1] += 1; player_y = ROOM_OFFSET_Y

        # Aktualizacja przeciwników
        for e in room["enemies"]:
            update_enemy_behavior(e, (player_x, player_y))
        
        # Sprawdzanie śmierci przeciwników
        room["enemies"] = [e for e in room["enemies"] if not handle_death(e)]

        # Rysowanie
        screen.fill(BLACK)
        draw_room(room)
        pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))
        draw_minimap()
        screen.blit(small_font.render(f"SEED: {current_seed}", True, WHITE), (20, 20))

    pygame.display.flip()

pygame.quit()