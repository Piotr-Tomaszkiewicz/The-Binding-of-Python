# enemydata.py
ENEMY_TYPES = {
    "D1": {"name": "Dummy", "hp": 100, "speed": 0, "flying": False, "size": 30, "behavior": "idle", "color": (255, 100, 100)},
    "C1": {"name": "Chaser", "hp": 30, "speed": 2.2, "flying": False, "size": 30, "behavior": "chase", "color": (200, 0, 0)},
    "C2": {"name": "Chaser 2", "hp": 26, "speed": 1.1, "flying": False, "size": 35, "behavior": "chase", "death_type": "explode", "color": (0, 100, 0)},
    "F1": {"name": "Flyer", "hp": 9, "speed": 1.76, "flying": True, "size": 20, "behavior": "chase", "color": (0, 0, 128)},
    "T1": {"name": "Turret", "hp": 19, "speed": 0, "flying": False, "size": 32, "behavior": "turret", "color": (255, 105, 180)},
    "T2": {"name": "Burster", "hp": 14, "speed": 0, "flying": False, "size": 32, "behavior": "burst_turret", "color": (148, 0, 211)},
    
    # BOSS B1 (Kolor łososiowy: 250, 128, 114)
    "B1": {
        "name": "Boss B1", "hp": 120, "speed": 2.25, "flying": False, "size": 60, 
        "behavior": "bounce", "split_to": "B1a", "color": (250, 128, 114)
    },
    "B1a": {
        "name": "B1 Mini", "hp": 60, "speed": 3.375, "flying": False, "size": 40, 
        "behavior": "bounce", "split_to": "B1b", "color": (250, 128, 114)
    },
    "B1b": {
        "name": "B1 Tiny", "hp": 30, "speed": 4.5, "flying": False, "size": 25, 
        "behavior": "bounce", "split_to": None, "color": (250, 128, 114)
    }
}