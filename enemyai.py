# enemyai.py
import math

def update_enemy_behavior(enemy, player_pos):
    """
    enemy: instancja klasy Enemy
    player_pos: (x, y) gracza
    """
    if enemy.behavior_type == "idle":
        # Dummy stoi w miejscu, nic nie robi
        pass
        
    elif enemy.behavior_type == "chase":
        # Przykład pogoni (na przyszłość)
        target_x, target_y = player_pos
        dx = target_x - enemy.rect.x
        dy = target_y - enemy.rect.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            enemy.rect.x += (dx / dist) * enemy.speed
            enemy.rect.y += (dy / dist) * enemy.speed

def handle_death(enemy):
    """Zwraca True jeśli przeciwnik powinien zostać usunięty"""
    if enemy.hp <= 0:
        print(f"Przeciwnik {enemy.name} zginął zwykłą śmiercią.")
        return True
    return False