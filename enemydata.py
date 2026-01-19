# enemydata.py
ENEMY_TYPES = {
    "D1": {
        "name": "Dummy",
        "hp": 100,
        "speed": 0,
        "flying": False,
        "behavior": "idle",
        "color": (255, 100, 100)
    },
    "C1": {
        "name": "Chaser",
        "hp": 30,
        "speed": 2.5,
        "flying": False,
        "behavior": "chase",
        "color": (200, 0, 0)
    }
}