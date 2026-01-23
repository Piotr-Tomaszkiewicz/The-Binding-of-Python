# enemyai.py
import math
import pygame
import heapq
import random

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

def check_enemy_tile_collision(rect, layout):
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
    off_x, off_y = (1280-640)//2, (720-640)//2
    
    if enemy.behavior_type == "bounce":
        # Wymaga, aby vx/vy zostały zainicjalizowane w main.py
        
        # Odbijanie od ścian i kamieni (z prostym odbiciem)
        if enemy.rect.left + enemy.vx < off_x or enemy.rect.right + enemy.vx > off_x + 640 or check_enemy_tile_collision(enemy.rect.move(enemy.vx, 0), layout):
            enemy.vx *= -1
        if enemy.rect.top + enemy.vy < off_y or enemy.rect.bottom + enemy.vy > off_y + 640 or check_enemy_tile_collision(enemy.rect.move(0, enemy.vy), layout):
            enemy.vy *= -1
        
        enemy.rect.x += enemy.vx
        enemy.rect.y += enemy.vy

    elif enemy.behavior_type == "bullet_hell":
        if not hasattr(enemy, 'shoot_mode'):
            enemy.shoot_mode = 0
            enemy.mode_timer = now
        
        if now - enemy.mode_timer > 4000:
            enemy.shoot_mode = 1 - enemy.shoot_mode
            enemy.mode_timer = now
            enemy.last_shot = 0 

        if enemy.shoot_mode == 0:
            if now - enemy.last_shot > 150:
                angle_offset = (now / 10) % 360
                for i in range(8):
                    angle = (i * 45) + angle_offset
                    rad = math.radians(angle)
                    enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, enemy.rect.centerx + math.cos(rad) * 100, enemy.rect.centery + math.sin(rad) * 100, 10))
                enemy.last_shot = now
                
        elif enemy.shoot_mode == 1:
            if now - enemy.last_shot > 800:
                angle_to_player = math.atan2(player_pos[1] + 15 - enemy.rect.centery, player_pos[0] + 15 - enemy.rect.centerx)
                for offset in [-0.2, -0.1, 0, 0.1, 0.2]:
                    rad = angle_to_player + offset
                    enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, enemy.rect.centerx + math.cos(rad) * 100, enemy.rect.centery + math.sin(rad) * 100, 10))
                enemy.last_shot = now

    elif enemy.behavior_type == "charger":
        if not hasattr(enemy, 'vx'):
            enemy.vx, enemy.vy = 0, 0
            enemy.mode_timer = now
            enemy.charging = False

        p_center_x, p_center_y = player_pos[0] + 15, player_pos[1] + 15
        e_center_x, e_center_y = enemy.rect.centerx, enemy.rect.centery
        
        if enemy.charging:
            hit_wall = False
            
            if enemy.rect.left + enemy.vx < off_x or enemy.rect.right + enemy.vx > off_x + 640 or check_enemy_tile_collision(enemy.rect.move(enemy.vx, 0), layout): hit_wall = True
            else: enemy.rect.x += enemy.vx
            
            if enemy.rect.top + enemy.vy < off_y or enemy.rect.bottom + enemy.vy > off_y + 640 or check_enemy_tile_collision(enemy.rect.move(0, enemy.vy), layout): hit_wall = True
            else: enemy.rect.y += enemy.vy
                
            if hit_wall:
                enemy.charging = False
                enemy.vx, enemy.vy = 0, 0
                enemy.mode_timer = now
                
        else:
            aligned_x = abs(p_center_x - e_center_x) < 30
            aligned_y = abs(p_center_y - e_center_y) < 30
            
            if aligned_x or aligned_y:
                enemy.charging = True
                charge_speed = enemy.speed * 2.0
                if aligned_x: 
                    enemy.vx = 0; enemy.vy = charge_speed * (1 if p_center_y > e_center_y else -1)
                elif aligned_y: 
                    enemy.vx = charge_speed * (1 if p_center_x > e_center_x else -1); enemy.vy = 0

            else: 
                if now - enemy.mode_timer > 1000:
                    enemy.mode_timer = now; angle = random.uniform(0, 2 * math.pi)
                    wander_speed = enemy.speed / 4 * 3.0
                    enemy.vx = math.cos(angle) * wander_speed; enemy.vy = math.sin(angle) * wander_speed
                
                if enemy.rect.left + enemy.vx < off_x or enemy.rect.right + enemy.vx > off_x + 640 or check_enemy_tile_collision(enemy.rect.move(enemy.vx, 0), layout): enemy.vx *= -1
                if enemy.rect.top + enemy.vy < off_y or enemy.rect.bottom + enemy.vy > off_y + 640 or check_enemy_tile_collision(enemy.rect.move(0, enemy.vy), layout): enemy.vy *= -1

                enemy.rect.x += enemy.vx
                enemy.rect.y += enemy.vy


    elif enemy.behavior_type == "turret":
        if now - enemy.last_shot > 1000:
            enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, player_pos[0]+15, player_pos[1]+15, 10))
            enemy.last_shot = now
            
    elif enemy.behavior_type == "burst_turret":
        if now - enemy.last_shot > 2000:
            dx = (player_pos[0]+15) - enemy.rect.centerx; dy = (player_pos[1]+15) - enemy.rect.centery; dist = math.hypot(dx, dy)
            if dist > 0:
                vx, vy = (dx/dist)*80, (dy/dist)*80
                new_rect = enemy.rect.move(vx, vy)
                if not check_enemy_tile_collision(new_rect, layout): enemy.rect.move_ip(vx, vy)
            for a in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(a); enemy_bullets.append(EnemyProjectile(enemy.rect.centerx, enemy.rect.centery, enemy.rect.centerx + math.cos(rad)*100, enemy.rect.centery + math.sin(rad)*100, 10))
            enemy.last_shot = now

    elif enemy.behavior_type == "chase":
        if enemy.flying: target_px, target_py = player_pos[0], player_pos[1]
        else:
            start = get_grid_pos(enemy.rect.centerx, enemy.rect.centery); goal = get_grid_pos(player_pos[0]+15, player_pos[1]+15)
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


def handle_death(enemy, room_explosions, current_enemies_list, EnemyClass):
    if enemy.hp <= 0:
        from enemydata import ENEMY_TYPES
        data = ENEMY_TYPES[enemy.id]
        
        if data.get("death_type") == "explode":
            room_explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
            
        split_id = data.get("split_to")
        if split_id:
            off_x, off_y = (1280-640)//2, (720-640)//2
            gx = (enemy.rect.centerx - off_x) // 40
            gy = (enemy.rect.centery - off_y) // 40
            e1 = EnemyClass(gx, gy, split_id); e2 = EnemyClass(gx, gy, split_id)
            current_enemies_list.extend([e1, e2])

        return True
    return False