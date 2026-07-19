"""dialogue_ops.py — Dead-End Detection (Fatia 4.8 / Etapa B8).

Valida dialogos e quests contra becos sem saida:
  - Nos de dialogo sem saida (folhas sem acao de conclusao)
  - Quests sem condicao de conclusao alcancavel
  - Ciclos infinitos em dialogos

Modela dialogo/quest como grafo direcionado e aplica DFS.
"""

import json
import re
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
