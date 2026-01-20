# items.py
import random

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
    },
    {
        "id": "roando",
        "name": "Roando",
        "is_special": True, "color": (240, 240, 240)
    },
    {
        "id": "aaa",
        "name": "AAA",
        "hp_up": 0, "heal": 0, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": 2.0,
        "bullet_size_mod": 0, "color": (255, 0, 0)
    },
    {
        "id": "blood_lust",
        "name": "Blood lust",
        "hp_up": 0, "heal": 0, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "color": (200, 0, 0)
    },
    {
        "id": "blessing",
        "name": "Blessing",
        "hp_up": 0, "heal": 0, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "color": (255, 255, 255)
    },
    {
        "id": "pierce",
        "name": "Pierce!",
        "hp_up": 0, "heal": 0, "dmg_up": 0.0, "fr_up": 0.0, "range_up": 0.0, "speed_up": 0.0,
        "bullet_size_mod": 0, "pierce_up": 1, "color": (150, 150, 150)
    }
]

def apply_item_stats(p_stats, item):
    if item.get("id") == "roando":
        roll = random.choice(["dmg", "hp", "speed", "range", "fr"])
        if roll == "dmg": p_stats["dmg"] += 3.0
        elif roll == "hp": 
            p_stats["max_hp"] += 1; p_stats["hp"] += 1
        elif roll == "speed": p_stats["speed"] += 2.0
        elif roll == "range": p_stats["range"] += 4.0
        elif roll == "fr": p_stats["fr"] += 1.0
    
    elif item.get("id") == "blessing":
        p_stats["inv_duration"] = 120
        
    else:
        p_stats["max_hp"] += item.get("hp_up", 0)
        p_stats["hp"] = min(p_stats["max_hp"], p_stats["hp"] + item.get("heal", 0))
        p_stats["dmg"] += item.get("dmg_up", 0)
        p_stats["fr"] += item.get("fr_up", 0)
        p_stats["range"] += item.get("range_up", 0)
        p_stats["speed"] += item.get("speed_up", 0)
        p_stats["pierce"] += item.get("pierce_up", 0)
        if item.get("bullet_size_mod", 0) > 0:
            p_stats["b_size_mult"] *= item["bullet_size_mod"]
    
    # Podłoga statystyk (minimum 1.0)
    for s in ["dmg", "fr", "range", "speed"]:
        p_stats[s] = max(1.0, p_stats[s])
        
    return p_stats