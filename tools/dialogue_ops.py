"""dialogue_ops.py — Dead-End Detection (Fatia 4.8 / Etapa B8).

Valida dialogos e quests contra becos sem saida:
  - Nos de dialogo sem saida (folhas sem acao de conclusao)
  - Quests sem condicao de conclusao alcancavel
  - Ciclos infinitos em dialogos

Modela dialogo/quest como grafo direcionado e aplica DFS.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _find_project_root(project_path: str | None = None) -> Path | None:
    if project_path:
        p = Path(project_path)
        if (p / "project.godot").exists():
            return p
        return None
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        pass
    if (ROOT / "project.godot").exists():
        return ROOT
    return None


def _read_gd_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════
# Op 1: find_dialogue_dead_ends
# ══════════════════════════════════════════════════════════════════════

def find_dialogue_dead_ends(
    dialogue_data: dict | None = None,
    project_path: str | None = None,
) -> dict:
    """Encontra becos sem saida em arvores de dialogo.

    Suporta formatos:
      - JSON de dialogo: {"nodes": [{"id":..., "text":..., "choices":[...], "next":...}]}
      - Dialogos extraidos de scripts .gd (formato dialogue_manager)

    Args:
        dialogue_data: Dados do dialogo em formato dict (opcional).
        project_path: Caminho do projeto para extracao automatica.

    Returns:
        dict com dead-ends encontrados e analise do grafo.
    """
    nodes = []

    if dialogue_data and "nodes" in dialogue_data:
        nodes = dialogue_data["nodes"]
    elif project_path:
        proj = _find_project_root(project_path)
        if proj:
            nodes = _extract_dialogue_from_project(proj)

    if not nodes:
        return {"status": "passed", "dead_ends": [], "total_nodes": 0,
                "detail": "Nenhum dialogo encontrado para analisar."}

    # Constroi grafo: node_id -> {text, outgoing: [target_ids]}
    graph = {}
    for n in nodes:
        nid = n.get("id", str(id(n)))
        outgoing = []

        # Coleta destinos via choices
        for choice in n.get("choices", []):
            if "next" in choice:
                outgoing.append(choice["next"])
            if "next_id" in choice:
                outgoing.append(str(choice["next_id"]))

        # Coleta destino direto (next)
        if "next" in n and n["next"] is not None:
            outgoing.append(str(n["next"]))
        if "next_id" in n and n["next_id"] is not None:
            outgoing.append(str(n["next_id"]))

        # Marca nos de saida (acao)
        is_exit = n.get("type") in ("exit", "end", "conclusion") or n.get("action") in ("close_dialogue", "end_dialogue", "complete_quest")

        graph[str(nid)] = {
            "text": str(n.get("text", ""))[:80],
            "outgoing": outgoing,
            "is_exit": is_exit,
        }

    # Encontra dead-ends: nos sem saida que nao sao exits
    dead_ends = []
    for nid, info in graph.items():
        if not info["outgoing"] and not info["is_exit"]:
            dead_ends.append({
                "node_id": nid,
                "text": info["text"],
                "issue": "dead_end",
                "detail": "No de dialogo sem saida — sem choices, sem next, sem acao de saida.",
                "severity": "error",
            })

    # Encontra nos inalcancaveis (sem incoming edges, exceto root)
    all_targets = set()
    for info in graph.values():
        for t in info["outgoing"]:
            all_targets.add(t)

    roots = [nid for nid in graph if nid not in all_targets]
    unreachable = [nid for nid in graph if nid not in all_targets]
    if roots:
        unreachable = [n for n in unreachable if n not in roots]

    for nid in unreachable:
        dead_ends.append({
            "node_id": nid,
            "text": graph[nid]["text"],
            "issue": "unreachable",
            "detail": "No inalcancavel — nenhum outro no referencia este ID.",
            "severity": "warning",
        })

    # Detecta ciclos
    cycles = _detect_cycles(graph)

    return {
        "status": "issues_found" if dead_ends else "passed",
        "total_nodes": len(graph),
        "dead_ends": dead_ends,
        "cycles": cycles,
        "roots": roots,
        "summary": f"{len(graph)} nos, {len(dead_ends)} dead-ends, {len(cycles)} ciclos",
    }


def _extract_dialogue_from_project(proj: Path) -> list[dict]:
    """Extrai definicoes de dialogo de arquivos JSON no projeto."""
    nodes = []

    # Procura JSON de dialogo em resources
    for fpath in proj.rglob("*.json"):
        if "dialogue" in fpath.name.lower() or "dialog" in fpath.name.lower():
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    nodes.extend(data)
                elif isinstance(data, dict) and "nodes" in data:
                    nodes.extend(data["nodes"])
            except Exception:
                pass

    return nodes


def _detect_cycles(graph: dict) -> list[dict]:
    """Detecta ciclos no grafo de dialogo via DFS."""
    cycles = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}

    def dfs(node: str, path: list[str]):
        color[node] = GRAY
        for neighbor in graph[node].get("outgoing", []):
            if neighbor not in color:
                continue  # referencia a no inexistente
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle = path[cycle_start:] + [neighbor]
                cycles.append({
                    "cycle": cycle,
                    "length": len(cycle),
                    "detail": f"Ciclo de {len(cycle)} nos: {' -> '.join(cycle)}",
                })
            elif color[neighbor] == WHITE:
                dfs(neighbor, path + [neighbor])
        color[node] = BLACK

    for node in graph:
        if color.get(node, BLACK) == WHITE:
            dfs(node, [node])

    return cycles


# ══════════════════════════════════════════════════════════════════════
# Op 2: validate_quest_completion
# ══════════════════════════════════════════════════════════════════════

def validate_quest_completion(
    quest_data: dict | None = None,
) -> dict:
    """Valida se uma quest possui caminho ate a conclusao.

    Verifica:
      - Existe pelo menos um passo de conclusao
      - Nao ha dependencias circulares
      - Todos os passos tem proximo passo ou acao definida

    Args:
        quest_data: Dados da quest (dict com steps/objectives).

    Returns:
        dict com resultado da validacao.
    """
    if quest_data is None:
        return {"status": "passed", "issues": [], "detail": "Nenhum dado de quest fornecido."}

    issues = []

    # Extrai passos/objetivos
    steps = quest_data.get("steps", quest_data.get("objectives", quest_data.get("nodes", [])))
    if not steps:
        return {"status": "passed", "issues": [], "detail": "Nenhum passo/objetivo encontrado."}

    # Encontra passo de conclusao
    has_conclusion = any(
        s.get("type") in ("complete", "conclusion", "end", "reward")
        or s.get("status") == "complete"
        for s in steps
    )

    if not has_conclusion:
        issues.append({
            "issue": "no_conclusion",
            "severity": "error",
            "detail": "Quest nao possui passo de conclusao. Jogador nunca termina a quest.",
        })

    # Verifica prerequisitos circulares
    for i, step in enumerate(steps):
        reqs = step.get("requires", step.get("prerequisites", []))
        step_id = step.get("id", str(i))
        for req in reqs:
            req_step = next((s for s in steps if s.get("id") == req), None)
            if req_step and req_step.get("requires", []):
                if step_id in req_step["requires"]:
                    issues.append({
                        "issue": "circular_dependency",
                        "severity": "error",
                        "detail": f"Dependencia circular: passo {step_id} requer {req} que requer {step_id}",
                    })

    # Verifica passos sem progressao
    for step in steps:
        sid = step.get("id", "?")
        has_next = step.get("next") or step.get("next_id") or step.get("completes_quest")
        has_action = step.get("action") or step.get("type") in ("dialogue", "combat", "collect", "deliver")
        if not has_next and not has_action and step.get("type") not in ("complete", "conclusion", "end"):
            issues.append({
                "issue": "dead_end_step",
                "severity": "warning",
                "step_id": sid,
                "detail": f"Passo '{sid}' nao tem proximo passo nem acao definida.",
            })

    return {
        "status": "issues_found" if issues else "passed",
        "total_steps": len(steps),
        "has_conclusion": has_conclusion,
        "issues": issues,
        "detail": f"{len(steps)} passos, {len(issues)} problemas",
    }


# ══════════════════════════════════════════════════════════════════
# NPC DIALOGUE GENERATION (Fatia 5.8)
# ══════════════════════════════════════════════════════════════════

_NPC_PERSONALITIES = {
    "guarda": {"tone": "formal", "topics": ["seguranca", "regras", "cidade"], "phrases": [
        "Atencao! Esta area e restrita.", "Nada para ver aqui, cidadao.", "Siga as regras e ninguem se machuca.",
        "Bom dia. Documentos, por favor.", "A patrulha esta tranquila hoje."
    ]},
    "mercador": {"tone": "amigavel", "topics": ["comercio", "itens", "precos"], "phrases": [
        "Ola, viajante! Tenho as melhores mercadorias!", "Veja so estas ofertas especiais.",
        "Compro e vendo de tudo.", "Nao encontrou o que queria? Volte amanha.",
        "Qualidade garantida — ou seu dinheiro de volta!"
    ]},
    "sabio": {"tone": "misterioso", "topics": ["conhecimento", "profecia", "magia"], "phrases": [
        "O universo sussurra segredos a quem sabe ouvir...", "Vejo grandes coisas no seu futuro.",
        "O conhecimento e a verdadeira riqueza.", "Nem toda pergunta merece resposta.",
        "A magia flui onde a vontade e forte."
    ]},
    "aldeao": {"tone": "simples", "topics": ["colheita", "clima", "fofoca"], "phrases": [
        "Ola, forasteiro!", "A colheita este ano foi boa.", "Ouvi dizer que tem monstros na floresta.",
        "Cuidado la fora — as estradas nao sao seguras.", "Bem-vindo a nossa humilde vila."
    ]},
    "vilao": {"tone": "ameacador", "topics": ["poder", "destruicao", "vinganca"], "phrases": [
        "Voce ousa me desafiar?", "Este mundo logo sera meu!", "Sua jornada termina aqui.",
        "Poder e tudo o que importa.", "Nao subestime minhas habilidades."
    ]},
    "companheiro": {"tone": "leal", "topics": ["aventura", "combate", "historia"], "phrases": [
        "Estou com voce ate o fim!", "Cuidado — tem inimigos a frente.", "Lembra daquela vez no castelo?",
        "Juntos somos mais fortes.", "Nao vou te abandonar."
    ]},
    "crianca": {"tone": "inocente", "topics": ["brincadeira", "sonhos", "curiosidade"], "phrases": [
        "Ola! Quer brincar?", "Voce e um heroi de verdade?", "Minha mae disse para nao falar com estranhos...",
        "Um dia quero ser aventureiro tambem!", "Viu o passarinho ali?"
    ]},
    "ancião": {"tone": "nostalgico", "topics": ["passado", "lendas", "conselhos"], "phrases": [
        "No meu tempo, as coisas eram diferentes...", "Deixe-me contar uma historia.",
        "A sabedoria vem com a idade.", "Conheci seu pai, sabia?", "Nao cometa os mesmos erros que eu."
    ]},
}

_DIALOGUE_SCENARIOS = {
    "greeting": ["Ola!", "Saudacoes.", "Bem-vindo.", "Oi, tudo bem?"],
    "farewell": ["Adeus.", "Ate logo.", "Va com cuidado.", "Volte sempre."],
    "quest_give": ["Preciso de ajuda com...", "Voce poderia fazer algo para mim?", "Ha uma tarefa urgente."],
    "quest_complete": ["Obrigado! Aqui esta sua recompensa.", "Missao cumprida!", "Voce e incrivel."],
    "combat_taunt": ["Prepare-se para lutar!", "Voce nao vai passar!", "E hora do combate!"],
    "fear": ["Socorro!", "Fuja enquanto pode!", "Isso e perigoso demais!"],
    "rumor": ["Ouvi dizer que...", "Ha boatos sobre...", "Voce ficou sabendo?"],
}


def dialogue_generate_npc_lines(args: dict | None = None) -> dict:
    """Gera linhas de dialogo para NPCs com personalidade (pre-geracao + cache).

    Usa templates por tipo de personalidade e cenarios de jogo.
    NAO usa LLM em runtime — as falas sao pre-geradas e cacheadas.
    Ideal para NPCs genericos de vilas, guardas, mercadores.

    Args:
        npc_type: Tipo de personalidade (guarda, mercador, sabio, aldeao, vilao,
                  companheiro, crianca, ancião). Default: "aldeao".
        scenario: Contexto (greeting, farewell, quest_give, quest_complete,
                  combat_taunt, fear, rumor). Default: "greeting".
        count: Quantas linhas gerar (max 10). Default: 3.
        npc_name: Nome do NPC para personalizar. Default: "".

    Returns:
        dict com lines (lista de falas), npc_type, scenario, tone.
    """
    args = args or {}
    npc_type = args.get("npc_type", "aldeao")
    scenario = args.get("scenario", "greeting")
    count = args.get("count")
    count = min(3 if count is None else count, 10)
    if count < 1:
        return {"status": "error", "message": "count deve ser >= 1."}
    npc_name = args.get("npc_name", "")

    if npc_type not in _NPC_PERSONALITIES:
        return {"status": "error", "message": f"Tipo desconhecido: {npc_type}. Opcoes: {list(_NPC_PERSONALITIES.keys())}"}

    personality = _NPC_PERSONALITIES[npc_type]
    scenario_phrases = _DIALOGUE_SCENARIOS.get(scenario, _DIALOGUE_SCENARIOS["greeting"])
    tone = personality["tone"]

    # Combina frases da personalidade + cenário
    import random
    rng = random.Random(args.get("seed", 42))
    pool = personality["phrases"] + scenario_phrases
    lines = rng.sample(pool, min(count, len(pool)))

    if npc_name:
        lines = [l.replace("viajante", npc_name).replace("forasteiro", npc_name).replace("cidadao", npc_name) for l in lines]

    return {
        "status": "success",
        "npc_type": npc_type,
        "npc_name": npc_name or "(generico)",
        "scenario": scenario,
        "tone": tone,
        "topics": personality["topics"],
        "lines": lines,
        "count": len(lines),
        "message": f"{len(lines)} linhas geradas para NPC {npc_type} ({tone}).",
    }


def dialogue_generate_personality(args: dict | None = None) -> dict:
    """Gera uma personalidade completa para um NPC (traços, motivações, falas).

    Cria um perfil de personagem com:
      - Traços de personalidade (Big Five simplificado)
      - Motivação principal
      - Medo/segredo
      - Relacionamento com o jogador
      - 5-10 falas características

    Args:
        npc_name: Nome do NPC.
        role: Papel no jogo (guarda, mercador, mentor, vilao, aliado, neutro).
        context: Breve descrição do contexto do NPC.

    Returns:
        dict com perfil completo de personalidade.
    """
    args = args or {}
    npc_name = args.get("npc_name", "NPC")
    role = args.get("role", "neutro")
    context = args.get("context", "")

    import random
    rng = random.Random(hash(npc_name + role + context) % (2**31))

    traits_pool = {
        "guarda": {"openness": 0.3, "conscientiousness": 0.9, "extraversion": 0.5, "agreeableness": 0.4, "neuroticism": 0.3},
        "mercador": {"openness": 0.6, "conscientiousness": 0.7, "extraversion": 0.8, "agreeableness": 0.7, "neuroticism": 0.2},
        "mentor": {"openness": 0.9, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.8, "neuroticism": 0.2},
        "vilao": {"openness": 0.5, "conscientiousness": 0.8, "extraversion": 0.7, "agreeableness": 0.1, "neuroticism": 0.6},
        "aliado": {"openness": 0.6, "conscientiousness": 0.6, "extraversion": 0.7, "agreeableness": 0.9, "neuroticism": 0.3},
        "neutro": {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.3},
    }

    motivations = ["poder", "riqueza", "conhecimento", "vinganca", "protecao", "redencao", "liberdade", "lealdade", "sobrevivencia", "legado"]
    fears = ["ser esquecido", "perder alguem", "fracassar", "traicao", "o desconhecido", "a propria forca", "ser substituido", "a verdade"]

    base_traits = traits_pool.get(role, traits_pool["neutro"])
    traits = {k: round(v + rng.uniform(-0.15, 0.15), 2) for k, v in base_traits.items()}
    motivation = rng.choice(motivations)
    fear = rng.choice(fears)

    return {
        "status": "success",
        "npc_name": npc_name,
        "role": role,
        "personality": {
            "traits": traits,
            "trait_labels": {k: "alto" if v > 0.6 else "baixo" if v < 0.4 else "medio" for k, v in traits.items()},
            "primary_motivation": motivation,
            "deepest_fear": fear,
            "relationship_to_player": {
                "guarda": "suspeito",
                "mercador": "cliente",
                "mentor": "protegido",
                "vilao": "inimigo",
                "aliado": "amigo",
                "neutro": "desconhecido",
            }.get(role, "neutro"),
        },
        "suggested_lines": dialogue_generate_npc_lines({
            "npc_type": "aldeao" if role in ("neutro", "aliado") else "guarda" if role == "guarda" else "vilao" if role == "vilao" else "sabio",
            "npc_name": npc_name,
            "scenario": "greeting",
            "count": 5,
            "seed": hash(npc_name + "seed") % (2**31),
        }).get("lines", []),
        "message": f"Personalidade gerada para {npc_name} ({role}).",
    }

