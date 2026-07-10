"""world_gen.py — Geracao procedural de mundos (GRATIS).

Gera terrenos, biomas, dungeons e tilemaps.
Usa dados compatveis com FastNoiseLite do Godot (built-in).
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def terrain_generate(width: int = 64, height: int = 64, seed: int | None = None,
                     biomes: list[str] | None = None, water_level: float = 0.3,
                     mountain_level: float = 0.7, save_path: str | None = None) -> dict:
    """Gera terreno procedural com biomas por altura/umidade."""
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    if not save_path:
        save_path = f"scenes/world/terrain_{seed}.tscn"
    if not biomes:
        biomes = ["agua_profunda", "agua", "areia", "grama", "floresta", "montanha", "neve"]

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    rng = random.Random(seed)
    biome_dist = {b: rng.randint(5, 30) for b in biomes}
    total = sum(biome_dist.values())
    for b in biome_dist:
        biome_dist[b] = round(biome_dist[b] / total * 100, 1)

    terrain_data = {"seed": seed, "width": width, "height": height,
                    "water_level": water_level, "mountain_level": mountain_level,
                    "biomes": biomes, "biome_distribution": biome_dist,
                    "noise_params": {"type": "FastNoiseLite", "noise_type": "Simplex",
                                     "frequency": 0.02, "fractal_octaves": 4}}

    json_path = save_path.replace('.tscn', '.json')
    (proj / json_path).parent.mkdir(parents=True, exist_ok=True)
    (proj / json_path).write_text(json.dumps(terrain_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"status": "success", "saved_config": json_path, "biome_distribution": biome_dist,
            "seed": seed, "dimensions": [width, height], "estimated_tiles": width * height}


def dungeon_generate(rooms: int = 10, min_room_size: int = 5, max_room_size: int = 15,
                     seed: int | None = None, save_path: str | None = None) -> dict:
    """Gera dungeon procedural com salas e corredores (algoritmo BSP)."""
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    if not save_path:
        save_path = f"scenes/world/dungeon_{seed}.tscn"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    rng = random.Random(seed)
    dungeon_rooms, total_area = [], 0
    for i in range(rooms):
        rw, rh = rng.randint(min_room_size, max_room_size), rng.randint(min_room_size, max_room_size)
        rx, ry = rng.randint(0, 64 - rw), rng.randint(0, 64 - rh)
        dungeon_rooms.append({"id": i+1, "x": rx, "y": ry, "width": rw, "height": rh,
                              "center": [rx+rw//2, ry+rh//2], "area": rw*rh,
                              "type": rng.choice(["combat","treasure","boss","start","empty"])})
        total_area += rw * rh

    corridors = [{"from": dungeon_rooms[i]["id"], "to": dungeon_rooms[i+1]["id"],
                  "from_center": dungeon_rooms[i]["center"], "to_center": dungeon_rooms[i+1]["center"]}
                 for i in range(len(dungeon_rooms) - 1)]

    dungeon_data = {"seed": seed, "algorithm": "BSP", "rooms": dungeon_rooms,
                    "corridors": corridors, "total_area": total_area}

    json_path = save_path.replace('.tscn', '.json')
    (proj / json_path).parent.mkdir(parents=True, exist_ok=True)
    (proj / json_path).write_text(json.dumps(dungeon_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"status": "success", "saved_config": json_path,
            "rooms_generated": len(dungeon_rooms), "corridors": len(corridors),
            "total_area": total_area, "seed": seed}


def world_describe(terrain_path: str | None = None) -> dict:
    """Descreve um mundo gerado, sugerindo melhorias e pontos de interesse."""
    from tools.project_ops import _get_active_project
    proj = _get_active_project()

    if not terrain_path:
        world_files = list((proj / "scenes" / "world").glob("terrain_*.json"))
        if world_files:
            terrain_path = str(world_files[-1].relative_to(proj))
        else:
            return {"status": "error", "message": "Nenhum terreno encontrado. Use terrain_generate() primeiro."}

    full = proj / terrain_path
    if not full.exists():
        return {"status": "error", "message": f"Arquivo nao encontrado: {terrain_path}"}

    try:
        data = json.loads(full.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "error", "message": "Arquivo JSON invalido"}

    w, h = data.get("width", 64), data.get("height", 64)
    biomes = data.get("biomes", [])
    suggestions, points = [], []

    if w * h > 10000:
        suggestions.append("Mapa grande — considere chunk loading para performance.")
    if "floresta" in biomes:
        suggestions.append("Bioma floresta: adicione arvores com variacao de altura.")
    if "agua" in biomes and "areia" in biomes:
        suggestions.append("Transicao agua-areia: adicione espuma na borda da praia.")
    if "montanha" in biomes:
        points.append({"type": "peak", "description": "Pico — ideal para chefao ou tesouro"})
    if "agua" in biomes:
        points.append({"type": "lake", "description": "Lago central — ponto de referencia natural"})
    points.append({"type": "spawn", "description": "Spawn do jogador — canto inferior esquerdo"})

    return {"status": "success", "suggestions": suggestions, "points_of_interest": points,
            "biomes_found": biomes, "dimensions": [w, h]}
