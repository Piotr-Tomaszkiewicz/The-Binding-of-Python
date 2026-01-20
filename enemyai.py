# enemyai.py
import math
import pygame
import heapq

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 100 
        self.timer = 20  
        self.active = True
        self.player_hit = False
        self.enemies_hit = []

    def update(self, p_rect, all_enemies):
        self.timer -= 1
        if self.timer <= 0: self.active = False
        player_damaged = False
        dist_p = math.hypot(self.x - p_rect.centerx, self.y - p_rect.centery)
        if dist_p < self.radius and not self.player_hit:
            self.player_hit = True
            player_damaged = True
        for e in all_enemies:
            if e not in self.enemies_hit:
                dist_e = math.hypot(self.x - e.rect.centerx, self.y - e.rect.centery)
                if dist_e < self.radius:
                    e.hp -= 13
                    self.enemies_hit.append(e)
        return player_damaged

    def draw(self, surface):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 165, 0, 160), (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))

class EnemyProjectile:
    def __init__(self, x, y, target_x, target_y, max_range):
        self.x, self.y = x, y
        self.speed = 5.5
        angle = math.atan2(target_y - y, target_x - x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.angle = math.degrees(angle)
        self.traveled = 0
        self.max_range_px = max_range * 40
        self.active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.traveled += self.speed
        if self.traveled > self.max_range_px:
            self.active = False

    def draw(self, surface):
        rad = math.radians(self.angle)
        p1 = (self.x + math.cos(rad)*14, self.y + math.sin(rad)*14)
        p2 = (self.x + math.cos(rad + 2.6)*9, self.y + math.sin(rad + 2.6)*9)
        p3 = (self.x + math.cos(rad - 2.6)*9, self.y + math.sin(rad - 2.6)*9)
        pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3])
        pygame.draw.polygon(surface, (255, 0, 0), [p1, p2, p3], 2)

def get_grid_pos(px, py):
    off_x, off_y = (1280-640)//2, (720-640)//2
    return int((px - off_x) // 40), int((py - off_y) // 40)

def check_enemy_tile_collision(rect, layout, flying):
    if flying: return False
    off_x, off_y = (1280-640)//2, (720-640)//2
    for y in range(16):
        for x in range(16):
            if layout[y][x] == 1:
                tile_rect = pygame.Rect(off_x + x*40, off_y + y*40, 40, 40)
                if rect.colliderect(tile_rect): return True
    return False

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

def update_enemy_behavior(enemy, player_pos, layout, all_enemies, enemy_bullets):
    now = pygame.time.get_ticks()
    if enemy.behavior_type == "idle": return
    
    elif enemy.behavior_type == "turret":
        if now - enemy.last_shot > 1000:
            enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, player_pos[0]+15, player_pos[1]+15, 10))
            enemy.last_shot = now
            
    elif enemy.behavior_type == "burst_turret":
        if now - enemy.last_shot > 2000: # Co 2 sekundy
            # 1. Ruch (skok o 2 kafelki = 80px)
            dx = (player_pos[0]+15) - enemy.rect.centerx
            dy = (player_pos[1]+15) - enemy.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                vx, vy = (dx/dist)*80, (dy/dist)*80
                new_rect = enemy.rect.move(vx, vy)
                if not check_enemy_tile_collision(new_rect, layout, enemy.flying):
                    enemy.rect.move_ip(vx, vy)
            
            # 2. Strzał w 8 stron
            angles = [0, 45, 90, 135, 180, 225, 270, 315]
            for a in angles:
                rad = math.radians(a)
                tx = enemy.rect.centerx + math.cos(rad)*100
                ty = enemy.rect.centery + math.sin(rad)*100
                enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, tx, ty, 10))
            
            enemy.last_shot = now

    elif enemy.behavior_type == "chase":
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