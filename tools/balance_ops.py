"""balance_ops.py — Auto-balancing para jogos (Onda de Refinamento).

Ferramentas para analisar e balancear jogos automaticamente:
    - balance_analyze: analisa jogo e sugere ajustes
    - wave_generate: gera composicao de ondas para tower defense
    - dps_calculator: calcula DPS, TTK, curvas de dano
    - loot_table_generate: gera tabelas de loot balanceadas
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════
# TOOL 1: balance_analyze
# ══════════════════════════════════════════════════════════════

def balance_analyze(
    game_type: str = "tower_defense",
    towers: list[dict] | None = None,
    enemies: list[dict] | None = None,
    waves: int = 30,
    target_duration_minutes: int = 15,
) -> dict:
    """Analisa o balanceamento do jogo e sugere ajustes.

    Args:
        game_type: Tipo de jogo (tower_defense, rpg, platformer, shooter).
        towers: Lista de torres. Cada uma:
            {"name": "Laser", "damage": 25, "fire_rate": 1.0, "range": 200, "cost": 100}
        enemies: Lista de inimigos. Cada um:
            {"name": "Scout", "hp": 50, "speed": 150, "reward": 10}
        waves: Numero total de waves.
        target_duration_minutes: Duracao alvo do jogo em minutos.

    Returns:
        {"status": "success", "analysis": {...}, "suggestions": [...], "curves": {...}}
    """
    if not towers:
        towers = [
            {"name": "Torre Basica", "damage": 20, "fire_rate": 1.0, "range": 150, "cost": 50},
            {"name": "Torre Laser", "damage": 40, "fire_rate": 0.5, "range": 200, "cost": 100},
            {"name": "Torre Foguete", "damage": 80, "fire_rate": 0.25, "range": 250, "cost": 200},
        ]

    if not enemies:
        enemies = [
            {"name": "Scout", "hp": 30, "speed": 150, "reward": 5},
            {"name": "Soldier", "hp": 80, "speed": 100, "reward": 15},
            {"name": "Tank", "hp": 250, "speed": 60, "reward": 40},
        ]

    analysis = {}

    # DPS de cada torre
    for t in towers:
        t["dps"] = t["damage"] * t["fire_rate"]
        t["cost_per_dps"] = t["cost"] / t["dps"] if t["dps"] > 0 else 999

    # HP total por wave (curva exponencial)
    base_hp = sum(e["hp"] for e in enemies) / len(enemies)
    hp_curve = []
    for w in range(1, waves + 1):
        multiplier = 1 + (w - 1) * 0.15
        hp_curve.append({
            "wave": w,
            "avg_enemy_hp": round(base_hp * multiplier),
            "total_hp_estimate": round(base_hp * multiplier * (3 + w * 0.5)),
        })

    # DPS necessario na wave final
    final_wave = hp_curve[-1]
    analysis["dps_needed_final_wave"] = round(final_wave["total_hp_estimate"] / (target_duration_minutes * 60 / waves))

    max_towers = 8
    max_dps = sum(t["dps"] for t in towers[:3]) * (max_towers / 3)
    analysis["max_possible_dps"] = round(max_dps)
    analysis["winnable"] = max_dps >= analysis["dps_needed_final_wave"]

    suggestions = []

    if not analysis["winnable"]:
        deficit = analysis["dps_needed_final_wave"] - max_dps
        suggestions.append({
            "priority": "critical",
            "problem": f"DPS maximo ({max_dps:.0f}) menor que necessario ({analysis['dps_needed_final_wave']:.0f})",
            "solution": f"Aumente dano das torres em {deficit/max_dps*100:.0f}% OU reduza HP dos inimigos finais",
            "specific": "Aumente damage da melhor torre de 80 para 120 OU reduza HP do Tank de 250 para 180",
        })

    for t in towers:
        avg_cpd = sum(x["cost_per_dps"] for x in towers) / len(towers)
        if t["cost_per_dps"] > avg_cpd * 1.5:
            suggestions.append({
                "priority": "balance",
                "problem": f"{t['name']} tem custo/DPS alto ({t['cost_per_dps']:.1f})",
                "solution": f"Reduza custo de {t['cost']} para {int(t['cost']*0.7)} OU aumente dano de {t['damage']} para {int(t['damage']*1.3)}",
            })

    for e in enemies:
        dps_of_best_tower = max(t["dps"] for t in towers)
        ttk = e["hp"] / dps_of_best_tower
        if ttk < 1:
            suggestions.append({
                "priority": "balance",
                "problem": f"{e['name']} morre muito rapido (TTK={ttk:.1f}s com melhor torre)",
                "solution": f"Aumente HP de {e['hp']} para {int(e['hp']*2)}",
            })
        elif ttk > 10:
            suggestions.append({
                "priority": "balance",
                "problem": f"{e['name']} demora muito para morrer (TTK={ttk:.1f}s)",
                "solution": f"Reduza HP de {e['hp']} para {int(e['hp']*0.7)}",
            })

    return {
        "status": "success",
        "analysis": analysis,
        "suggestions": suggestions,
        "hp_curve": hp_curve,
        "tower_stats": towers,
        "enemy_stats": enemies,
    }


# ══════════════════════════════════════════════════════════════
# TOOL 2: wave_generate
# ══════════════════════════════════════════════════════════════

def wave_generate(
    wave_count: int = 30,
    enemy_types: list[dict] | None = None,
    difficulty_curve: str = "exponential",
    boss_every: int = 10,
) -> dict:
    """Gera composicao de ondas para tower defense.

    Args:
        wave_count: Numero total de ondas.
        enemy_types: Tipos de inimigos disponiveis.
            [{"name": "Scout", "base_count": 5, "weight": 1.0, "min_wave": 1}]
        difficulty_curve: "linear", "exponential", "staircase".
        boss_every: A cada quantas waves colocar um chefao.

    Returns:
        {"status": "success", "waves": [{wave, enemies: [{type, count}]}, ...]}
    """
    if not enemy_types:
        enemy_types = [
            {"name": "Scout", "base_count": 5, "weight": 1.0, "min_wave": 1, "hp_mult": 1.0},
            {"name": "Soldier", "base_count": 2, "weight": 1.5, "min_wave": 3, "hp_mult": 2.0},
            {"name": "Tank", "base_count": 1, "weight": 3.0, "min_wave": 8, "hp_mult": 5.0},
            {"name": "Speeder", "base_count": 3, "weight": 1.2, "min_wave": 5, "hp_mult": 0.8},
        ]

    waves = []

    for w in range(1, wave_count + 1):
        if difficulty_curve == "linear":
            diff = 1 + (w - 1) * 0.1
        elif difficulty_curve == "staircase":
            diff = 1 + (w // 5) * 0.5
        else:
            diff = math.pow(1.12, w - 1)

        available = [e for e in enemy_types if e["min_wave"] <= w]
        total_weight = sum(e["weight"] for e in available)
        wave_enemies = []

        for enemy in available:
            proportion = enemy["weight"] / total_weight
            count = max(0, round(enemy["base_count"] * diff * proportion))
            if count > 0:
                wave_enemies.append({
                    "type": enemy["name"],
                    "count": count,
                    "hp_multiplier": round(enemy["hp_mult"] * diff, 2),
                })

        is_boss = (w % boss_every == 0)
        boss = None
        if is_boss and w > 1:
            boss = {
                "name": f"Boss Wave {w}",
                "hp_multiplier": round(diff * 3, 1),
                "special_ability": "Enrage at 50% HP" if w % 20 == 0 else "Summons minions",
            }

        waves.append({
            "wave": w,
            "difficulty_multiplier": round(diff, 2),
            "enemies": wave_enemies,
            "total_enemies": sum(e["count"] for e in wave_enemies),
            "is_boss_wave": is_boss,
            "boss": boss,
        })

    return {
        "status": "success",
        "waves": waves,
        "total_waves": wave_count,
        "total_enemies_all_waves": sum(w["total_enemies"] for w in waves),
        "boss_waves": [w["wave"] for w in waves if w["is_boss_wave"]],
    }


# ══════════════════════════════════════════════════════════════
# TOOL 3: dps_calculator
# ══════════════════════════════════════════════════════════════

def dps_calculator(
    damage: float,
    fire_rate: float,
    crit_chance: float = 0.0,
    crit_multiplier: float = 2.0,
    aoe_radius: float = 0.0,
    aoe_targets: int = 1,
    damage_over_time: float = 0.0,
    dot_duration: float = 0.0,
) -> dict:
    """Calcula DPS efetivo considerando criticos, area e dano continuo.

    Args:
        damage: Dano base por ataque.
        fire_rate: Ataques por segundo.
        crit_chance: Chance de critico (0 a 1).
        crit_multiplier: Multiplicador de dano critico.
        aoe_radius: Raio de area (0 = single target).
        aoe_targets: Inimigos medios atingidos por area.
        damage_over_time: Dano por segundo de DoT.
        dot_duration: Duracao do DoT em segundos.

    Returns:
        {"status": "success", "effective_dps": 145, "ttk": {...}}
    """
    base_dps = damage * fire_rate
    crit_mult = 1 + crit_chance * (crit_multiplier - 1)
    crit_dps = base_dps * crit_mult
    aoe_dps = crit_dps * max(1, aoe_targets) if aoe_radius > 0 else crit_dps
    dot_total = damage_over_time * dot_duration if dot_duration > 0 else 0
    effective_dps = aoe_dps + (dot_total * fire_rate)

    ttk = {}
    for hp in [50, 100, 250, 500, 1000]:
        if effective_dps > 0:
            ttk[f"{hp}hp"] = round(hp / effective_dps, 2)

    return {
        "status": "success",
        "base_dps": round(base_dps, 1),
        "crit_multiplied_dps": round(crit_dps, 1),
        "aoe_dps": round(aoe_dps, 1),
        "effective_dps": round(effective_dps, 1),
        "breakdown": {
            "base": f"{damage} dmg x {fire_rate}/s = {base_dps:.0f}",
            "crit": f"+{(crit_dps - base_dps):.0f} ({(crit_chance*100):.0f}% x {crit_multiplier}x)",
            "aoe": f"x{max(1, aoe_targets)} targets" if aoe_radius > 0 else "single target",
            "dot": f"+{dot_total:.0f} over {dot_duration}s" if dot_duration > 0 else "none",
        },
        "ttk": ttk,
    }


# ══════════════════════════════════════════════════════════════
# TOOL 4: loot_table_generate
# ══════════════════════════════════════════════════════════════

def loot_table_generate(
    rarity_levels: list[str] | None = None,
    items_per_rarity: int = 5,
    game_theme: str = "scifi",
) -> dict:
    """Gera tabela de loot balanceada por raridade.

    Args:
        rarity_levels: Lista de raridades. Default: ["Comum", "Incomum", "Raro", "Epico", "Lendario"].
        items_per_rarity: Quantos itens por raridade.
        game_theme: Tema do jogo (scifi, fantasy, modern, post_apocalyptic).

    Returns:
        {"status": "success", "loot_table": [...], "drop_chances": {...}}
    """
    if not rarity_levels:
        rarity_levels = ["Comum", "Incomum", "Raro", "Epico", "Lendario"]

    drop_chances = {
        "Comum": 50.0,
        "Incomum": 30.0,
        "Raro": 13.0,
        "Epico": 5.5,
        "Lendario": 1.5,
    }

    themes = {
        "scifi": {
            "prefixes": ["Plasma", "Quantum", "Foton", "Ionico", "Nanite", "Tesla", "Fase", "Dark Matter"],
            "items": ["Coil", "Capacitor", "Lente", "Reator", "Emissor", "Nucleo", "Matriz", "Cristal"],
            "stats": ["dano", "velocidade_de_ataque", "alcance", "critico", "efeito_em_area"],
        },
        "fantasy": {
            "prefixes": ["Runico", "Elfico", "Draconico", "Sagrado", "Arcana", "Elemental", "Ancestral"],
            "items": ["Gema", "Pergaminho", "Amuleto", "Anel", "Cetro", "Orbe", "Cajado"],
            "stats": ["dano_magico", "cura", "escudo", "velocidade", "mana"],
        },
        "modern": {
            "prefixes": ["Tatico", "Precision", "Tatico", "Reforcado", "Otimizado"],
            "items": ["Mira", "Silenciador", "Carregador", "Empunhadura", "Municao"],
            "stats": ["dano", "precisao", "cadencia", "recarga", "estabilidade"],
        },
        "post_apocalyptic": {
            "prefixes": ["Enferrujado", "Improvisado", "Reciclado", "Mutante", "Radioativo"],
            "items": ["Sucata", "Peca", "Mola", "Tubo", "Engrenagem", "Bateria", "Fusivel"],
            "stats": ["dano", "durabilidade", "sorte", "residuo_radioativo", "fome"],
        },
    }

    theme = themes.get(game_theme, themes["scifi"])

    loot_table = []
    for rarity in rarity_levels:
        for i in range(items_per_rarity):
            prefix = theme["prefixes"][(hash(rarity + str(i) + "p") % len(theme["prefixes"]))]
            item_name = theme["items"][(hash(rarity + str(i) + "n") % len(theme["items"]))]
            stat = theme["stats"][(hash(rarity + str(i) + "s") % len(theme["stats"]))]

            rarity_index = rarity_levels.index(rarity)
            stat_value = round(5 * (1.5 ** rarity_index) * (0.8 + 0.4 * ((hash(rarity + str(i) + prefix) % 100) / 100)), 1)

            loot_table.append({
                "name": f"{prefix} {item_name}",
                "rarity": rarity,
                "stat": stat,
                "stat_value": stat_value,
                "drop_chance": f"{drop_chances.get(rarity, 1) / items_per_rarity:.2f}%",
            })

    return {
        "status": "success",
        "loot_table": loot_table,
        "total_items": len(loot_table),
        "drop_chances_summary": drop_chances,
        "theme": game_theme,
    }


# ══════════════════════════════════════════════════════════════
# TOOL 5: gdd_generate (ONDA 2 — GRATIS)
# ══════════════════════════════════════════════════════════════

def gdd_generate(
    concept: str,
    game_type: str = "tower_defense",
    target_platform: str = "pc",
    detail_level: str = "full",
) -> dict:
    """Gera Game Design Document (GDD) completo a partir de uma ideia.

    Args:
        concept: Ideia do jogo em uma frase.
            Ex: "tower defense sci-fi com 5 torres elementais e chefoes a cada 10 waves"
        game_type: Tipo de jogo (tower_defense, platformer, rpg, shooter, puzzle, roguelike).
        target_platform: Plataforma alvo (pc, mobile, web).
        detail_level: Nivel de detalhe (brief = 1 pagina, full = documento completo).

    Returns:
        {"status": "success", "gdd": {...}, "sections": [...]}
    """
    import hashlib
    import random

    seed = int(hashlib.md5(concept.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    type_templates = {
        "tower_defense": {
            "core_loop": "Posicionar torres -> Inimigos avancam -> Torres atacam -> Coletar recursos -> Melhorar torres -> Proxima wave",
            "mechanics": ["Posicionamento estrategico em grid", "Inimigos seguem waypoints",
                "Torres atacam automaticamente", "Recursos por inimigo derrotado",
                "Upgrade de torres", "Habilidades especiais com cooldown"],
            "win_condition": "Sobreviver a todas as waves sem deixar inimigos alcancarem a base",
            "lose_condition": "Inimigos alcancam a base e destroem o nucleo",
            "metrics": ["DPS", "alcance", "custo", "velocidade de ataque", "HP inimigos", "velocidade inimigos"],
        },
        "platformer": {
            "core_loop": "Explorar fase -> Pular obstaculos -> Derrotar inimigos -> Coletar itens -> Chegar ao fim",
            "mechanics": ["Movimento lateral com pulo", "Fisica de gravidade",
                "Power-ups temporarios", "Checkpoints", "Segredos e areas escondidas"],
            "win_condition": "Chegar ao final da fase",
            "lose_condition": "Perder todas as vidas",
            "metrics": ["velocidade", "altura do pulo", "dano", "vidas", "tempo"],
        },
        "rpg": {
            "core_loop": "Explorar mundo -> Encontrar inimigos -> Batalhar -> Ganhar XP -> Upgradear",
            "mechanics": ["Sistema de nivel e experiencia", "Arvore de habilidades",
                "Inventario e equipamentos", "Dialogos com NPCs", "Quests principais e secundarias"],
            "win_condition": "Derrotar o chefao final",
            "lose_condition": "Game over (perder todo HP)",
            "metrics": ["HP", "MP", "ATK", "DEF", "SPD", "nivel"],
        },
        "shooter": {
            "core_loop": "Mover -> Mirar -> Atirar -> Eliminar inimigos -> Avancar",
            "mechanics": ["Movimento WASD + mouse", "Armas variadas",
                "Sistema de cobertura", "Recarga e municao", "Headshots e dano critico"],
            "win_condition": "Eliminar todos os inimigos da fase",
            "lose_condition": "Morrer",
            "metrics": ["dano", "cadencia", "precisao", "municao", "vida"],
        },
        "puzzle": {
            "core_loop": "Observar -> Raciocinar -> Mover pecas -> Resolver -> Proximo nivel",
            "mechanics": ["Mecanica central unica", "Dificuldade progressiva",
                "Dicas opcionais", "Sistema de pontuacao (estrelas)"],
            "win_condition": "Resolver o puzzle",
            "lose_condition": "Desistir ou ficar sem movimentos",
            "metrics": ["movimentos", "tempo", "estrelas", "dicas usadas"],
        },
        "roguelike": {
            "core_loop": "Entrar dungeon -> Explorar salas -> Combater -> Coletar loot -> Morrer -> Renascer mais forte",
            "mechanics": ["Geracao procedural de salas", "Permadeath com meta-progressao",
                "Itens e habilidades aleatorias", "Builds e sinergias", "Chefoes por bioma"],
            "win_condition": "Derrotar o chefao final em uma run",
            "lose_condition": "Morrer (mas mantem progresso meta)",
            "metrics": ["HP", "dano", "velocidade", "sorte", "ouro"],
        },
    }

    template = type_templates.get(game_type, type_templates["tower_defense"])

    prefixes = {
        "tower_defense": ["Defense of", "Siege of", "Guardians of", "Last Stand:", "Hold the"],
        "platformer": ["Super", "Mega", "Ultra", "Jump:", "Adventures of"],
        "rpg": ["Chronicles of", "Legend of", "Tales of", "Age of", "Realms of"],
        "shooter": ["Operation:", "Strike:", "Assault:", "Combat:", "Warzone:"],
        "puzzle": ["The Mystery of", "Puzzle:", "Enigma:", "Riddle of", "Connect:"],
        "roguelike": ["Dungeons of", "Depths of", "Void:", "Runs of", "Eternal"],
    }

    prefix = rng.choice(prefixes.get(game_type, prefixes["tower_defense"]))
    title = f"{prefix} {concept[:40]}"

    gdd = {
        "title": title,
        "concept": concept,
        "genre": game_type.replace("_", " ").title(),
        "platform": target_platform,
        "elevator_pitch": f"Um jogo de {game_type.replace('_', ' ')} onde {concept}",
        "target_audience": "Fas de jogos de estrategia e sci-fi" if game_type == "tower_defense" else "Jogadores casuais e hardcore",
        "gameplay": {
            "core_loop": template["core_loop"],
            "mechanics": template["mechanics"],
            "controls": _gdd_controls(game_type, target_platform),
            "progression": _gdd_progression(game_type),
        },
        "win_lose": {"win": template["win_condition"], "lose": template["lose_condition"]},
        "balance": {
            "metrics": template["metrics"],
            "difficulty_curve": "Facil nas primeiras fases, aumenta progressivamente, pico nos chefoes",
            "economy": _gdd_economy(game_type),
        },
        "content_scope": {
            "estimated_levels": 30 if game_type == "tower_defense" else 20,
            "enemy_types": "8-12 tipos com variacoes",
            "bosses": "1 chefao a cada 10 niveis" if game_type == "tower_defense" else "1 chefao por bioma",
            "items_powerups": "15-20 itens/power-ups",
            "estimated_playtime": "2-4 horas para campanha principal",
        },
        "technical": {
            "engine": "Godot 4.7",
            "language": "GDScript",
            "resolution": "1920x1080 (escalavel)",
            "target_fps": 60,
            "art_style": "Pixel art 32x32" if rng.random() > 0.5 else "2D cartoon estilizado",
            "audio": "SFX procedural + musica de fundo",
        },
    }

    if detail_level == "full":
        gdd["story"] = _gdd_story(concept, game_type)
        gdd["monetization"] = _gdd_monetization(target_platform)
        gdd["marketing"] = _gdd_marketing(title, game_type)
        gdd["development_roadmap"] = _gdd_roadmap()

    return {
        "status": "success",
        "gdd": gdd,
        "sections": list(gdd.keys()),
        "detail_level": detail_level,
        "message": f"GDD gerado com {len(gdd)} secoes. Use balance_analyze() para validar o balanceamento.",
    }


def _gdd_controls(game_type, platform):
    if platform == "mobile":
        return {"type": "touch", "description": "Toque na tela para posicionar/controlar"}
    return {"type": "keyboard+mouse", "keys": {"WASD": "Movimento", "Mouse": "Mirar/Selecionar", "Espaco": "Acao/Pulo"}}

def _gdd_progression(game_type):
    return {"tower_defense": "30 waves com dificuldade crescente", "platformer": "5 mundos com 5 fases cada",
            "rpg": "Level 1-50. Novas areas por nivel e quests."}.get(game_type, "Progressao linear com picos de dificuldade.")

def _gdd_economy(game_type):
    return {"tower_defense": "Ouro por inimigo derrotado. Bonus por wave completa sem dano.",
            "rpg": "Ouro de inimigos e quests. Lojas em cada cidade."}.get(game_type, "Recursos ganhos ao completar objetivos.")

def _gdd_story(concept, game_type):
    return {"premise": f"Em um mundo onde {concept}, o jogador deve...",
            "setting": "Universo sci-fi" if "sci-fi" in concept.lower() else "Mundo de fantasia",
            "characters": ["Protagonista", "Aliado mentor", "Vilao principal", "NPCs de suporte"],
            "tone": "Epico e imersivo com momentos de tensao"}

def _gdd_monetization(platform):
    return "Free-to-play com cosmeticos" if platform == "mobile" else "Premium (preco unico). DLCs futuras."

def _gdd_marketing(title, game_type):
    return {"tagline": f"{title} — {game_type.replace('_', ' ').title()} como voce nunca viu",
            "key_features": ["Mecanica inovadora", "Visual unico", "Trilha imersiva", "Alta rejogabilidade"],
            "target_stores": ["Steam", "itch.io"]}

def _gdd_roadmap():
    return [{"phase": "Pre-producao", "duration": "2 semanas", "tasks": ["GDD finalizado", "Prototipo", "Arte conceitual"]},
            {"phase": "Producao", "duration": "8 semanas", "tasks": ["Mecanicas principais", "Assets finais", "Level design"]},
            {"phase": "Polimento", "duration": "2 semanas", "tasks": ["Balanceamento", "Bug fixing", "Otimizacao"]},
            {"phase": "Lancamento", "duration": "1 semana", "tasks": ["Build final", "Store pages", "Marketing"]}]
