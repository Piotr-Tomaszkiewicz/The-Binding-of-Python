import pygame
import random
import math

from roomdata import ROOM_TEMPLATES
from enemydata import ENEMY_TYPES
from enemyai import update_enemy_behavior, handle_death, Explosion, EnemyProjectile

pygame.init()

# --- KONFIGURACJA ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
TILE_SIZE = 40  
ROOM_DIM = 16
ROOM_WIDTH_PX = ROOM_DIM * TILE_SIZE
ROOM_HEIGHT_PX = ROOM_DIM * TILE_SIZE
ROOM_OFFSET_X = (SCREEN_WIDTH - ROOM_WIDTH_PX) // 2
ROOM_OFFSET_Y = (SCREEN_HEIGHT - ROOM_HEIGHT_PX) // 2

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
GREEN, RED, YELLOW, BLUE = (100, 255, 100), (255, 50, 50), (255, 255, 0), (0, 100, 255)
GRAY, DARK_GRAY = (160, 160, 160), (60, 60, 60)
MINIMAP_BG = (30, 30, 30)

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("The Binding of Python")
clock = pygame.time.Clock()

menu_font = pygame.font.SysFont('Arial', 40, bold=True)
stats_font = pygame.font.SysFont('Arial', 24, bold=True)

# --- STATYSTYKI ---
player_max_hp = 3
player_hp = 3
player_dmg = 5
player_fr = 2.0      
player_range = 6.0   
player_speed_tiles = 6.0 
player_inv_timer = 0     

class Projectile:
    def __init__(self, x, y, direction, dmg, max_range):
        self.x, self.y = x, y
        self.dir = direction
        self.dmg = dmg
        self.speed = 10.0
        self.traveled = 0
        self.max_range_px = max_range * TILE_SIZE
        self.active = True

    def update(self):
        mx, my = self.dir[0] * self.speed, self.dir[1] * self.speed
        self.x += mx; self.y += my
        self.traveled += math.hypot(mx, my)
        if self.traveled > self.max_range_px: self.active = False

    def draw(self, surface):
        cx, cy = self.x, self.y
        if self.dir == (0, -1): pts = [(cx, cy-10), (cx-7, cy+5), (cx+7, cy+5)]
        elif self.dir == (0, 1): pts = [(cx, cy+10), (cx-7, cy-5), (cx+7, cy-5)]
        elif self.dir == (-1, 0): pts = [(cx-10, cy), (cx+5, cy-7), (cx+5, cy+7)]
        else: pts = [(cx+10, cy), (cx-5, cy-7), (cx-5, cy+7)]
        pygame.draw.polygon(surface, WHITE, pts)

class Enemy:
    def __init__(self, x_grid, y_grid, enemy_id):
        data = ENEMY_TYPES[enemy_id]
        self.id = enemy_id
        self.max_hp = data["hp"]; self.hp = data["hp"]
        self.speed = data["speed"]; self.color = data["color"]
        self.behavior_type = data["behavior"]; self.flying = data["flying"]
        self.size = data.get("size", 30)
        self.last_shot = 0 # Dla Turretów
        px = ROOM_OFFSET_X + x_grid*TILE_SIZE + (TILE_SIZE - self.size)//2
        py = ROOM_OFFSET_Y + y_grid*TILE_SIZE + (TILE_SIZE - self.size)//2
        self.rect = pygame.Rect(px, py, self.size, self.size)

def get_pixel_speed(): return (player_speed_tiles * TILE_SIZE) / 60

def generate_map():
    grid = [[0 for _ in range(9)] for _ in range(9)]
    grid[4][4] = 4; rooms = [(4, 4)]
    for _ in range(6):
        px, py = random.choice(rooms)
        dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        nx, ny = px+dx, py+dy
        if 0 <= nx < 9 and 0 <= ny < 9 and grid[ny][nx] == 0:
            grid[ny][nx] = 1; rooms.append((nx, ny))
    candidates = [(x,y) for y in range(9) for x in range(9) if grid[y][x] == 0 and sum(1 for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)] if 0<=x+dx<9 and 0<=y+dy<9 and grid[y+dy][x+dx]!=0) == 1]
    random.shuffle(candidates)
    if len(candidates) >= 2: grid[candidates[0][1]][candidates[0][0]] = 2; grid[candidates[1][1]][candidates[1][0]] = 3
    final_map = {}
    for y in range(9):
        for x in range(9):
            rtype = grid[y][x]
            if rtype != 0:
                layout = [[0]*16 for _ in range(16)]
                enemies = []
                if rtype == 1:
                    raw = random.choice(ROOM_TEMPLATES)
                    for ly in range(16):
                        for lx in range(16):
                            if raw[ly][lx] == 1: layout[ly][lx] = 1
                            elif isinstance(raw[ly][lx], str) and raw[ly][lx] in ENEMY_TYPES:
                                enemies.append(Enemy(lx, ly, raw[ly][lx]))
                final_map[(x, y)] = {"type": rtype, "layout": layout, "enemies": enemies, "explosions": [], "enemy_bullets": []}
    return final_map

def check_tile_collision(rect, layout):
    for y in range(16):
        for x in range(16):
            if layout[y][x] == 1:
                r = pygame.Rect(ROOM_OFFSET_X + x*40, ROOM_OFFSET_Y + y*40, 40, 40)
                if rect.colliderect(r): return True
    return False

def draw_ui():
    for i in range(player_max_hp):
        pos = (40 + i * 35, 40)
        pygame.draw.circle(screen, WHITE, pos, 14, 2)
        pygame.draw.circle(screen, RED if i < player_hp else BLACK, pos, 12)
    stats = [f"DMG: {player_dmg}", f"FR: {player_fr}", f"RANGE: {player_range}", f"SPEED: {player_speed_tiles}"]
    for i, txt in enumerate(stats): screen.blit(stats_font.render(txt, True, WHITE), (25, 80 + i * 30))

def draw_room(room_data):
    layout = room_data["layout"]
    locked = len(room_data["enemies"]) > 0
    door_color = DARK_GRAY if locked else BLUE
    for y in range(16):
        for x in range(16):
            r = pygame.Rect(ROOM_OFFSET_X + x*40, ROOM_OFFSET_Y + y*40, 40, 40)
            pygame.draw.rect(screen, (40, 40, 40), r)
            pygame.draw.rect(screen, (30, 30, 30), r, 1)
            if layout[y][x] == 1: pygame.draw.rect(screen, GRAY, r.inflate(-4, -4))
    rx, ry = current_room
    for dx, dy, side in [(0,-1,"top"), (0,1,"bottom"), (-1,0,"left"), (1,0,"right")]:
        if (rx+dx, ry+dy) in game_map:
            if side == "top": pygame.draw.line(screen, door_color, (ROOM_OFFSET_X+280, ROOM_OFFSET_Y), (ROOM_OFFSET_X+360, ROOM_OFFSET_Y), 10)
            elif side == "bottom": pygame.draw.line(screen, door_color, (ROOM_OFFSET_X+280, ROOM_OFFSET_Y+640), (ROOM_OFFSET_X+360, ROOM_OFFSET_Y+640), 10)
            elif side == "left": pygame.draw.line(screen, door_color, (ROOM_OFFSET_X, ROOM_OFFSET_Y+280), (ROOM_OFFSET_X, ROOM_OFFSET_Y+360), 10)
            elif side == "right": pygame.draw.line(screen, door_color, (ROOM_OFFSET_X+640, ROOM_OFFSET_Y+280), (ROOM_OFFSET_X+640, ROOM_OFFSET_Y+360), 10)

def draw_minimap():
    ms = 12; ox, oy = SCREEN_WIDTH - 140, 25
    pygame.draw.rect(screen, MINIMAP_BG, (ox-5, oy-5, 9*ms+10, 9*ms+10))
    for (x,y), data in game_map.items():
        c = WHITE
        if data["type"] == 2: c = YELLOW
        if data["type"] == 3: c = RED
        if data["type"] == 4: c = (150, 150, 255)
        if [x,y] == current_room: c = (0, 255, 0)
        pygame.draw.rect(screen, c, (ox+x*ms, oy+y*ms, ms-1, ms-1))

scene = 0; running = True; game_map = {}; current_room = [4, 4]
player_x, player_y = 0.0, 0.0; player_bullets = []; last_shot_time = 0; player_size = 30
btn_start = pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-80, 240, 60)
btn_quit = pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+20, 240, 60)

def start_new_game():
    global scene, game_map, current_room, player_x, player_y, player_hp, player_bullets, player_inv_timer
    game_map = generate_map(); current_room = [4, 4]
    player_x, player_y = SCREEN_WIDTH//2-15, SCREEN_HEIGHT//2-15
    player_hp = 3; player_inv_timer = 0; player_bullets = []; scene = 1

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and scene == 0:
            if btn_start.collidepoint(event.pos): start_new_game()
            if btn_quit.collidepoint(event.pos): running = False

    if scene == 0:
        screen.fill(WHITE)
        pygame.draw.rect(screen, GREEN, btn_start, border_radius=12); pygame.draw.rect(screen, RED, btn_quit, border_radius=12)
        txt_s = menu_font.render("START", True, BLACK); txt_q = menu_font.render("QUIT", True, BLACK)
        screen.blit(txt_s, txt_s.get_rect(center=btn_start.center)); screen.blit(txt_q, txt_q.get_rect(center=btn_quit.center))

    elif scene == 1:
        keys = pygame.key.get_pressed(); speed = get_pixel_speed()
        room = game_map[tuple(current_room)]
        locked = len(room["enemies"]) > 0
        if player_inv_timer > 0: player_inv_timer -= 1
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= speed
        if keys[pygame.K_s]: dy += speed
        if keys[pygame.K_a]: dx -= speed
        if keys[pygame.K_d]: dx += speed
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        
        # Ruch
        new_x_rect = pygame.Rect(player_x + dx, player_y, player_size, player_size)
        if not check_tile_collision(new_x_rect, room["layout"]):
            if ROOM_OFFSET_X <= new_x_rect.x <= ROOM_OFFSET_X + 640 - player_size: player_x += dx
            elif 280 < (player_y - ROOM_OFFSET_Y) < 360 and not locked:
                if new_x_rect.x < ROOM_OFFSET_X and (current_room[0]-1, current_room[1]) in game_map:
                    current_room[0]-=1; player_x=ROOM_OFFSET_X+640-player_size; player_bullets=[]; room["enemy_bullets"]=[]
                elif new_x_rect.x > ROOM_OFFSET_X+640-player_size and (current_room[0]+1, current_room[1]) in game_map:
                    current_room[0]+=1; player_x=ROOM_OFFSET_X; player_bullets=[]; room["enemy_bullets"]=[]

        new_y_rect = pygame.Rect(player_x, player_y + dy, player_size, player_size)
        if not check_tile_collision(new_y_rect, room["layout"]):
            if ROOM_OFFSET_Y <= new_y_rect.y <= ROOM_OFFSET_Y + 640 - player_size: player_y += dy
            elif 280 < (player_x - ROOM_OFFSET_X) < 360 and not locked:
                if new_y_rect.y < ROOM_OFFSET_Y and (current_room[0], current_room[1]-1) in game_map:
                    current_room[1]-=1; player_y=ROOM_OFFSET_Y+640-player_size; player_bullets=[]; room["enemy_bullets"]=[]
                elif new_y_rect.y > ROOM_OFFSET_Y+640-player_size and (current_room[0], current_room[1]+1) in game_map:
                    current_room[1]+=1; player_y=ROOM_OFFSET_Y; player_bullets=[]; room["enemy_bullets"]=[]

        # Strzelanie Gracza
        now = pygame.time.get_ticks(); s_dir = None
        if keys[pygame.K_UP]: s_dir = (0, -1)
        elif keys[pygame.K_DOWN]: s_dir = (0, 1)
        elif keys[pygame.K_LEFT]: s_dir = (-1, 0)
        elif keys[pygame.K_RIGHT]: s_dir = (1, 0)
        if s_dir and now - last_shot_time > 1000 / player_fr:
            player_bullets.append(Projectile(player_x+15, player_y+15, s_dir, player_dmg, player_range)); last_shot_time = now

        # Pociski Gracza
        for b in player_bullets[:]:
            b.update()
            if not (ROOM_OFFSET_X < b.x < ROOM_OFFSET_X+640 and ROOM_OFFSET_Y < b.y < ROOM_OFFSET_Y+640): b.active=False
            gx, gy = int((b.x-ROOM_OFFSET_X)//40), int((b.y-ROOM_OFFSET_Y)//40)
            if 0<=gx<16 and 0<=gy<16 and room["layout"][gy][gx]==1: b.active=False
            for e in room["enemies"]:
                if e.rect.collidepoint(b.x, b.y): e.hp-=b.dmg; b.active=False
            if not b.active: player_bullets.remove(b)

        # Pociski Przeciwników
        for eb in room["enemy_bullets"][:]:
            eb.update()
            # Ściany
            if not (ROOM_OFFSET_X < eb.x < ROOM_OFFSET_X+640 and ROOM_OFFSET_Y < eb.y < ROOM_OFFSET_Y+640): eb.active=False
            # Kamienie
            gx, gy = int((eb.x-ROOM_OFFSET_X)//40), int((eb.y-ROOM_OFFSET_Y)//40)
            if 0<=gx<16 and 0<=gy<16 and room["layout"][gy][gx]==1: eb.active=False
            # Gracz
            if eb.active and p_rect.collidepoint(eb.x, eb.y):
                if player_inv_timer == 0:
                    player_hp -= 1; player_inv_timer = 60
                eb.active = False
            if not eb.active: room["enemy_bullets"].remove(eb)

        # Eksplozje
        for ex in room["explosions"][:]:
            if ex.update(p_rect, room["enemies"]) and player_inv_timer == 0:
                player_hp -= 1; player_inv_timer = 60
            if not ex.active: room["explosions"].remove(ex)

        # AI
        for e in room["enemies"]:
            update_enemy_behavior(e, (player_x, player_y), room["layout"], room["enemies"], room["enemy_bullets"])
            if player_inv_timer == 0 and p_rect.colliderect(e.rect):
                player_hp -= 1; player_inv_timer = 60
        
        room["enemies"] = [e for e in room["enemies"] if not handle_death(e, room["explosions"])]
        if player_hp <= 0: scene = 0

        # RYSOWANIE
        screen.fill(BLACK); draw_room(room)
        for b in player_bullets: b.draw(screen)
        for e in room["enemies"]:
            pygame.draw.rect(screen, e.color, e.rect)
            pygame.draw.rect(screen, RED, (e.rect.x, e.rect.y-8, e.rect.width, 4))
            pygame.draw.rect(screen, GREEN, (e.rect.x, e.rect.y-8, (e.hp/e.max_hp)*e.rect.width, 4))
        
        if player_inv_timer % 10 < 5: pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, 30, 30))
        
        # Pociski wrogów i wybuchy na samym wierzchu
        for ex in room["explosions"]: ex.draw(screen)
        for eb in room["enemy_bullets"]: eb.draw(screen)
            
        draw_ui(); draw_minimap()

    pygame.display.flip()
pygame.quit()