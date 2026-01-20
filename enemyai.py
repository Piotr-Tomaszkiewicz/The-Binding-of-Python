# enemyai.py
import math
import pygame
import heapq

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 100 # 2.5 tile (2.5 * 40)
        self.timer = 20  # czas trwania w klatkach
        self.active = True
        self.player_hit = False
        self.enemies_hit = [] # Lista ID/obiektów trafionych wrogów

    def update(self, p_rect, enemies):
        self.timer -= 1
        if self.timer <= 0: self.active = False
        
        # 1. Kolizja z graczem (1 HP)
        player_damaged = False
        dist_p = math.hypot(self.x - p_rect.centerx, self.y - p_rect.centery)
        if dist_p < self.radius and not self.player_hit:
            self.player_hit = True
            player_damaged = True # Sygnał dla main.py

        # 2. Kolizja z innymi wrogami (13 HP)
        for e in enemies:
            if e not in self.enemies_hit:
                dist_e = math.hypot(self.x - e.rect.centerx, self.y - e.rect.centery)
                if dist_e < self.radius:
                    e.hp -= 13
                    self.enemies_hit.append(e)
                    
        return player_damaged

    def draw(self, surface):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        # Pomarańczowe koło (lekko powiększone wizualnie)
        pygame.draw.circle(s, (255, 100, 0, 160), (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))

def get_grid_pos(px, py):
    off_x, off_y = (1280-640)//2, (720-640)//2
    return int((px - off_x) // 40), int((py - off_y) // 40)

def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(start, goal, layout):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set(); came_from = {}; gscore = {start:0}; fscore = {start:h(start,goal)}
    oheap = [(fscore[start], start)]
    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            p = []
            while current in came_from: p.append(current); current = came_from[current]
            return p[::-1]
        close_set.add(current)
        for i, j in neighbors:
            nb = current[0]+i, current[1]+j
            if 0<=nb[0]<16 and 0<=nb[1]<16 and layout[nb[1]][nb[0]]!=1 and nb not in close_set:
                tg = gscore[current]+1
                if nb not in gscore or tg < gscore[nb]:
                    came_from[nb]=current; gscore[nb]=tg; fscore[nb]=tg+h(nb,goal)
                    heapq.heappush(oheap, (fscore[nb], nb))
    return []

def update_enemy_behavior(enemy, player_pos, layout, all_enemies):
    if enemy.behavior_type == "idle": return
    if enemy.flying: target_px, target_py = player_pos[0], player_pos[1]
    else:
        start = get_grid_pos(enemy.rect.centerx, enemy.rect.centery)
        goal = get_grid_pos(player_pos[0]+15, player_pos[1]+15)
        path = a_star(start, goal, layout)
        if not path: target_px, target_py = player_pos[0], player_pos[1]
        else:
            off_x, off_y = (1280-640)//2, (720-640)//2
            target_px = off_x + path[0][0]*40 + (40-enemy.rect.width)//2
            target_py = off_y + path[0][1]*40 + (40-enemy.rect.height)//2
    dx, dy = target_px - enemy.rect.x, target_py - enemy.rect.y
    dist = math.hypot(dx, dy)
    if dist > 0:
        vx, vy = (dx/dist)*enemy.speed, (dy/dist)*enemy.speed
        nx = enemy.rect.move(vx, 0)
        if not any(other != enemy and nx.colliderect(other.rect) for other in all_enemies): enemy.rect.x += vx
        ny = enemy.rect.move(0, vy)
        if not any(other != enemy and ny.colliderect(other.rect) for other in all_enemies): enemy.rect.y += vy

def handle_death(enemy, room_explosions):
    if enemy.hp <= 0:
        from enemydata import ENEMY_TYPES
        if ENEMY_TYPES[enemy.id].get("death_type") == "explode":
            room_explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
        return True
    return False