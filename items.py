# items.py

ITEM_POOL = [
    {
        "id": "armata",
        "name": "Armata",
        "hp_up": 0, "heal": 0, "dmg_up": 3.0, "fr_up": -0.3, "range_up": 2.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "color": (100, 100, 100)
    },
    {
        "id": "crystal_heart",
        "name": "Crystal heart",
        "hp_up": 1, "heal": 1, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "color": (0, 255, 255)
    },
    {
        "id": "chubby",
        "name": "Chubby",
        "hp_up": 1, "heal": 0, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": -0.4,
        "bullet_size_mod": 1.5, "color": (200, 150, 100)
    },
    {
        "id": "karate",
        "name": "Karate",
        "hp_up": 0, "heal": 0, "dmg_up": 0.0, "fr_up": 2.0, "range_up": -3.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "color": (255, 220, 180)
    }
]

def apply_item_stats(p_stats, item):
    """Aplikuje statystyki przedmiotu z limitem dolnym 1.0"""
    p_stats["max_hp"] += item.get("hp_up", 0)
    p_stats["hp"] = min(p_stats["max_hp"], p_stats["hp"] + item.get("heal", 0))
    
    # Statystyki z limitem minimum 1.0
    p_stats["dmg"] = max(1.0, p_stats["dmg"] + item.get("dmg_up", 0))
    p_stats["fr"] = max(1.0, p_stats["fr"] + item.get("fr_up", 0))
    p_stats["range"] = max(1.0, p_stats["range"] + item.get("range_up", 0))
    p_stats["speed"] = max(1.0, p_stats["speed"] + item.get("speed_up", 0))
    
    # Chubby modyfikator wielkości pocisku
    if item.get("bullet_size_mod") > 0:
        p_stats["b_size_mult"] *= item["bullet_size_mod"]
        
    return p_stats