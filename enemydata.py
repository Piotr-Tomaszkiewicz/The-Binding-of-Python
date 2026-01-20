# enemydata.py
ENEMY_TYPES = {
    "D1": {
        "name": "Dummy", "hp": 100, "speed": 0, "flying": False, "size": 30,
        "behavior": "idle", "color": (255, 100, 100)
    },
    "C1": {
        "name": "Chaser", "hp": 30, "speed": 2.2, "flying": False, "size": 30,
        "behavior": "chase", "color": (200, 0, 0)
    },
    "C2": {
        "name": "Chaser 2", "hp": 26, "speed": 1.1, "flying": False, "size": 35,
        "behavior": "chase", "death_type": "explode", "color": (0, 100, 0) # Ciemnozielony
    },
    "F1": {
        "name": "Flyer", "hp": 9, "speed": 1.76, "flying": True, "size": 20,
        "behavior": "chase", "color": (0, 0, 128)
    }
}