# enemyai.py
import math
import pygame
import heapq

def get_grid_pos(px, py):
    OFFSET_X = (1280 - 16 * 40) // 2
    OFFSET_Y = (720 - 16 * 40) // 2
    gx = int((px - OFFSET_X) // 40)
    gy = int((py - OFFSET_Y) // 40)
    return gx, gy

def a_star(start, goal, layout):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = [(fscore[start], start)]

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < 16 and 0 <= neighbor[1] < 16:
                if layout[neighbor[1]][neighbor[0]] == 1: continue
            else: continue
            if neighbor in close_set: continue
            tentative_g_score = gscore[current] + 1
            if neighbor not in gscore or tentative_g_score < gscore[neighbor]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return []

def check_enemy_collisions(enemy, next_rect, all_enemies):
    """Sprawdza, czy nowy prostokąt przeciwnika koliduje z innymi przeciwnikami."""
    for other in all_enemies:
        if other is not enemy: # Nie sprawdzaj kolizji ze samym sobą
            if next_rect.colliderect(other.rect):
                return True
    return False

def update_enemy_behavior(enemy, player_pos, layout, all_enemies):
    if enemy.behavior_type == "idle":
        pass

    elif enemy.behavior_type == "chase":
        start = get_grid_pos(enemy.rect.centerx, enemy.rect.centery)
        goal = get_grid_pos(player_pos[0] + 15, player_pos[1] + 15)

        if start == goal:
            target_px, target_py = player_pos[0], player_pos[1]
        else:
            path = a_star(start, goal, layout)
            if not path: return
            next_tile = path[0]
            OFFSET_X = (1280 - 16 * 40) // 2
            OFFSET_Y = (720 - 16 * 40) // 2
            target_px = OFFSET_X + next_tile[0] * 40 + 5
            target_py = OFFSET_Y + next_tile[1] * 40 + 5

        dx = target_px - enemy.rect.x
        dy = target_py - enemy.rect.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            vx = (dx / dist) * enemy.speed
            vy = (dy / dist) * enemy.speed

            # Ruch X z kolizją
            new_rect_x = enemy.rect.move(vx, 0)
            if not check_enemy_collisions(enemy, new_rect_x, all_enemies):
                # Tutaj można by też dodać check_tile_collision jeśli chcemy być pewni
                enemy.rect.x += vx
            
            # Ruch Y z kolizją
            new_rect_y = enemy.rect.move(0, vy)
            if not check_enemy_collisions(enemy, new_rect_y, all_enemies):
                enemy.rect.y += vy

def handle_death(enemy):
    return enemy.hp <= 0