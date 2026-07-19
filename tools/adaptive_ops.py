"""adaptive_ops.py — Dificuldade Adaptativa + Quest + Balance (Fatia 5.5).

Ferramentas para ajuste dinâmico de gameplay:
  - Dificuldade adaptativa baseada em desempenho do jogador
  - Geração procedural de quests
  - Configuração de balance remoto
  - Validação de branches de diálogo/quest
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def adaptive_difficulty_adjust(args: dict | None = None) -> dict:
    """Analisa desempenho do jogador e sugere ajustes de dificuldade.

    Usa métricas (mortes, tempo por fase, kills, dano) para
    recomendar ajustes em: vida do inimigo, dano, spawn rate,
    velocidade, drops.

    Args:
        player_metrics: Métricas do jogador {deaths, kills, time_per_level, damage_taken, accuracy}.
        current_difficulty: Dificuldade atual (easy, normal, hard).
        target_win_rate: Taxa de vitória desejada (0.0-1.0, default: 0.6).

    Returns:
        dict com ajustes recomendados e nova dificuldade.
    """
    args = args or {}
    metrics = args.get("player_metrics", {})
    current_difficulty = args.get("current_difficulty", "normal")
    target_win_rate = args.get("target_win_rate", 0.6)

    if not metrics:
        metrics = {"deaths": 3, "kills": 25, "time_per_level_sec": 180, "damage_taken": 45, "accuracy": 0.7}

    deaths = metrics.get("deaths", 0)
    kills = metrics.get("kills", 0)
    time_per_level = metrics.get("time_per_level_sec", 180)
    damage_taken = metrics.get("damage_taken", 0)
    accuracy = metrics.get("accuracy", 0.5)

    adjustments = []
    new_difficulty = current_difficulty

    # Análise de dificuldade
    if deaths > 5 and time_per_level > 300:
        adjustments.append({"parameter": "enemy_health", "change": "-20%", "reason": "Muitas mortes e fase lenta."})
        adjustments.append({"parameter": "enemy_damage", "change": "-15%", "reason": "Jogador toma muito dano."})
        new_difficulty = "easy" if current_difficulty == "normal" else current_difficulty
    elif deaths <= 1 and accuracy > 0.8 and time_per_level < 120:
        adjustments.append({"parameter": "enemy_health", "change": "+25%", "reason": "Jogador muito eficiente."})
        adjustments.append({"parameter": "spawn_rate", "change": "+20%", "reason": "Fase completada rapido demais."})
        new_difficulty = "hard" if current_difficulty == "normal" else current_difficulty
    else:
        adjustments.append({"parameter": "none", "change": "0%", "reason": "Desempenho dentro do esperado."})

    if damage_taken > 50:
        adjustments.append({"parameter": "drop_rate_health", "change": "+15%", "reason": "Jogador precisa de mais cura."})

    return {
        "status": "success",
        "player_metrics": metrics,
        "current_difficulty": current_difficulty,
        "recommended_difficulty": new_difficulty,
        "target_win_rate": target_win_rate,
        "adjustments": adjustments,
        "message": f"Dificuldade sugerida: {new_difficulty} ({len(adjustments)} ajustes).",
    }


def quest_generate(args: dict | None = None) -> dict:
    """Gera uma quest procedural baseada em templates.

    Cria uma quest com:
      - Título e descrição
      - Objetivo principal
      - Objetivos opcionais (bônus)
      - Recompensas
      - Diálogo de NPC (give + complete)

    Args:
        quest_type: Tipo (fetch, kill, escort, collect, boss, explore).
        difficulty: Dificuldade (easy, normal, hard).
        level_range: Nível recomendado (min, max).
        npc_giver: Nome do NPC que dá a quest.

    Returns:
        dict com quest completa.
    """
    args = args or {}
    quest_type = args.get("quest_type", "fetch")
    difficulty = args.get("difficulty", "normal")
    level_range = args.get("level_range", [1, 5])
    npc_giver = args.get("npc_giver", "Aldeão")

    import random
    rng = random.Random(args.get("seed", 42))

    quest_templates = {
        "fetch": {
            "title_prefix": ["Buscar ", "Recuperar ", "Coletar ", "Encontrar "],
            "items": ["Erva Medicinal", "Cristal Mágico", "Pergaminho Antigo", "Chave Enferrujada", "Gema Brilhante"],
            "location": ["na Floresta Sombria", "na Caverna Profunda", "no Templo Abandonado", "no Acampamento Inimigo"],
            "objectives": ["Colete {item} {location}", "Entregue para {npc}"],
            "rewards": {"xp": 100, "gold": 50, "item": "Poção de Cura"},
        },
        "kill": {
            "title_prefix": ["Eliminar ", "Derrotar ", "Caçar ", "Acabar com "],
            "targets": ["Slimes", "Lobos", "Esqueletos", "Bandidos", "Aranhas Gigantes"],
            "location": ["na Floresta", "nas Montanhas", "no Cemitério", "na Estrada"],
            "objectives": ["Derrote {count} {target} {location}", "Retorne para {npc}"],
            "rewards": {"xp": 150, "gold": 75, "item": "Espada de Ferro"},
        },
        "boss": {
            "title_prefix": ["Confrontar ", "Desafiar ", "Enfrentar "],
            "targets": ["Dragão Ancião", "Lorde das Trevas", "Golem de Pedra", "Rei Demônio"],
            "location": ["no Castelo", "na Masmorra", "no Vulcão", "na Torre"],
            "objectives": ["Derrote {target} {location}", "Colete o troféu como prova"],
            "rewards": {"xp": 500, "gold": 300, "item": "Armadura Lendária"},
        },
        "explore": {
            "title_prefix": ["Explorar ", "Mapear ", "Descobrir "],
            "locations": ["Ruínas Antigas", "Floresta Encantada", "Caverna de Cristal", "Ilha Perdida"],
            "objectives": ["Explore {location}", "Encontre {count} pontos de interesse", "Retorne e relate"],
            "rewards": {"xp": 120, "gold": 60, "item": "Mapa do Tesouro"},
        },
    }

    template = quest_templates.get(quest_type, quest_templates["fetch"])
    title = rng.choice(template["title_prefix"])

    if quest_type == "fetch":
        item = rng.choice(template["items"])
        location = rng.choice(template["location"])
        title += item
        objectives = [obj.format(item=item, location=location, npc=npc_giver, count=rng.randint(3, 8)) for obj in template["objectives"]]
    elif quest_type in ("kill",):
        target = rng.choice(template["targets"])
        location = rng.choice(template["location"])
        title += target
        objectives = [obj.format(target=target, location=location, count=rng.randint(3, 10), npc=npc_giver) for obj in template["objectives"]]
    elif quest_type == "boss":
        target = rng.choice(template["targets"])
        location = rng.choice(template["location"])
        title += target
        objectives = [obj.format(target=target, location=location) for obj in template["objectives"]]
    else:
        location = rng.choice(template["locations"])
        title += location
        objectives = [obj.format(location=location, count=rng.randint(3, 6)) for obj in template["objectives"]]

    if not level_range:
        return {"status": "error", "message": "level_range nao pode ser vazio."}
    level = rng.randint(*level_range) if len(level_range) >= 2 else level_range[0]
    rewards = template["rewards"].copy()
    if difficulty == "hard":
        rewards["xp"] = int(rewards["xp"] * 1.5)
        rewards["gold"] = int(rewards["gold"] * 1.5)
    elif difficulty == "easy":
        rewards["xp"] = int(rewards["xp"] * 0.7)
        rewards["gold"] = int(rewards["gold"] * 0.7)

    return {
        "status": "success",
        "quest": {
            "title": title,
            "type": quest_type,
            "difficulty": difficulty,
            "level": level,
            "npc_giver": npc_giver,
            "objectives": objectives,
            "bonus_objectives": [f"Complete sem morrer", f"Complete em menos de {rng.randint(3, 8)} minutos"],
            "rewards": rewards,
            "dialogue_give": f"'{npc_giver}: {title}? Preciso de alguem corajoso...'",
            "dialogue_complete": f"'{npc_giver}: Incrivel! Voce conseguiu! Aqui esta sua recompensa.'",
        },
        "message": f"Quest '{title}' gerada ({quest_type}, lv{level}).",
    }


def remote_balance_config(args: dict | None = None) -> dict:
    """Gerencia configuração de balance remoto para ajustes pós-lançamento.

    Permite definir valores de balance que podem ser atualizados
    sem patch (via arquivo JSON remoto ou CDN).

    Args:
        action: "export" (gerar JSON), "template" (criar template), "validate" (validar JSON).
        config: Dicionário de configuração (para validate).

    Returns:
        dict com configuração de balance exportada ou validada.
    """
    args = args or {}
    action = args.get("action", "template")
    config = args.get("config", {})

    template = {
        "_meta": {"version": "1.0", "updated": "", "description": "Remote balance config — atualizado sem patch."},
        "enemies": {
            "slime": {"health": 20, "damage": 5, "speed": 100, "xp_reward": 10},
            "skeleton": {"health": 40, "damage": 12, "speed": 80, "xp_reward": 25},
            "boss_dragon": {"health": 500, "damage": 30, "speed": 60, "xp_reward": 200},
        },
        "weapons": {
            "sword": {"damage": 10, "attack_speed": 1.0, "range": 40},
            "bow": {"damage": 7, "attack_speed": 0.6, "range": 300},
        },
        "economy": {
            "coin_drop_rate": 0.3,
            "health_potion_cost": 25,
            "upgrade_cost_multiplier": 1.5,
        },
        "difficulty_presets": {
            "easy": {"enemy_health_mult": 0.7, "enemy_damage_mult": 0.6, "drop_rate_mult": 1.3},
            "normal": {"enemy_health_mult": 1.0, "enemy_damage_mult": 1.0, "drop_rate_mult": 1.0},
            "hard": {"enemy_health_mult": 1.5, "enemy_damage_mult": 1.4, "drop_rate_mult": 0.8},
        },
    }

    if action == "template":
        return {"status": "success", "action": "template", "template": template, "message": "Template de config de balance gerado."}

    if action == "export":
        import json, datetime
        export = template.copy()
        export["_meta"]["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"status": "success", "action": "export", "config_json": json.dumps(export, indent=2, ensure_ascii=False), "message": "Config de balance exportada."}

    if action == "validate":
        if not config:
            return {"status": "error", "message": "Forneca 'config' para validar."}
        issues = []
        if "enemies" not in config:
            issues.append("Falta seção 'enemies'.")
        if "difficulty_presets" not in config:
            issues.append("Falta seção 'difficulty_presets'.")
        presets = config.get("difficulty_presets", {})
        for name in ["easy", "normal", "hard"]:
            if name not in presets:
                issues.append(f"Falta preset de dificuldade: {name}.")
        return {
            "status": "success" if not issues else "issues_found",
            "action": "validate",
            "valid": len(issues) == 0,
            "issues": issues,
            "message": f"Validacao: {'OK' if not issues else f'{len(issues)} problemas'}.",
        }

    return {"status": "error", "message": f"Acao desconhecida: {action}. Use template, export ou validate."}
