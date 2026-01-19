# enemydata.py
ENEMY_TYPES = {
    "D1": {
        "name": "Dummy",
        "hp": 100,
        "speed": 0,
        "flying": False,
        "behavior": "idle", # Typ zachowania
        "color": (255, 100, 100)
    },
    "S1": { # Przykład na przyszłość
        "name": "Chaser",
        "hp": 20,
        "speed": 2,
        "flying": False,
        "behavior": "chase",
        "color": (200, 0, 0)
    }
}