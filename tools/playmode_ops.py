"""playmode_ops.py — Play Mode Automation (Fase 2C / B7).

Assertions e sequências de input para teste automatizado de gameplay.
Inspirado no FunplayAI.

Tools:
    - assert_node_exists: verifica se nó existe na cena
    - assert_node_property: verifica valor de propriedade
    - simulate_input_sequence: injeta sequência de inputs
"""

import json
import time
from pathlib import Path


def assert_node_exists(
    scene_path: str,
    node_path: str,
    node_type: str | None = None,
) -> dict:
    """Verifica se um nó existe em uma cena.

    Args:
        scene_path: Caminho da cena .tscn.
        node_path: Path do nó (ex: "./Player/Camera2D").
        node_type: Tipo esperado do nó (opcional).

    Returns:
        dict com resultado da assertion.
    """
    from tools.scene_ops import load_scene_tree

    try:
        result = load_scene_tree(scene_path)
        tree = result.get("tree", result) if isinstance(result, dict) else {}
        if isinstance(result, dict) and result.get("status") == "error":
            return {"status": "fail", "assertion": "node_exists", "message": f"Cena não carregada: {scene_path}"}

        # Navega recursivamente na árvore (estrutura: {name, type, children: [...]})
        def _find_node(n, target_path):
            clean = target_path.lstrip("./")
            path_parts = [p for p in clean.split("/") if p] if clean else []
            if not path_parts:
                return n  # "." = raiz
            # Se o primeiro segmento bate com o nome do nó atual, começa daqui
            if n.get("name") == path_parts[0]:
                path_parts = path_parts[1:]
                if not path_parts:
                    return n
            current = n
            for part in path_parts:
                children = current.get("children", [])
                found = None
                for child in children:
                    if child.get("name") == part:
                        found = child
                        break
                if not found:
                    return None
                current = found
            return current

        found = _find_node(tree, node_path)

        if not found:
            # Coleta paths disponíveis para o erro
            available = []
            def _collect_paths(n, prefix=""):
                name = n.get("name", "?")
                p = f"{prefix}/{name}" if prefix else name
                available.append(p)
                for c in n.get("children", []):
                    _collect_paths(c, p)
            _collect_paths(tree)
            return {
                "status": "fail",
                "assertion": "node_exists",
                "node": node_path,
                "message": f"Nó '{node_path}' não encontrado na cena",
                "available_nodes": available[:15],
            }

        if node_type and found.get("type") != node_type:
            return {
                "status": "fail",
                "assertion": "node_exists",
                "node": node_path,
                "message": f"Tipo esperado '{node_type}', encontrado '{found.get('type')}'",
            }

        return {
            "status": "pass",
            "assertion": "node_exists",
            "node": node_path,
            "type": found.get("type"),
        }
    except Exception as e:
        return {"status": "error", "assertion": "node_exists", "message": str(e)}


def assert_node_property(
    scene_path: str,
    node_path: str,
    property_name: str,
    expected_value: str | None = None,
    value_type: str | None = None,
) -> dict:
    """Verifica o valor de uma propriedade de nó.

    Args:
        scene_path: Caminho da cena.
        node_path: Path do nó.
        property_name: Nome da propriedade.
        expected_value: Valor esperado (string). Se None, só verifica existência.
        value_type: Tipo esperado (ex: "Vector2", "int", "String").

    Returns:
        dict com resultado.
    """
    from tools.scene_ops import get_node_property

    try:
        result = get_node_property(scene_path, node_path, property_name)
        if result.get("status") != "success":
            return {
                "status": "fail",
                "assertion": "node_property",
                "node": node_path,
                "property": property_name,
                "message": result.get("message", "Propriedade não encontrada"),
            }

        actual = str(result.get("value", ""))

        if value_type:
            actual_type = type(result.get("value")).__name__
            if actual_type != value_type:
                return {
                    "status": "fail",
                    "assertion": "node_property",
                    "node": node_path,
                    "property": property_name,
                    "expected_type": value_type,
                    "actual_type": actual_type,
                    "message": f"Tipo esperado '{value_type}', obtido '{actual_type}'",
                }

        if expected_value is not None and actual != str(expected_value):
            return {
                "status": "fail",
                "assertion": "node_property",
                "node": node_path,
                "property": property_name,
                "expected": expected_value,
                "actual": actual,
                "message": f"Valor esperado '{expected_value}', obtido '{actual}'",
            }

        return {
            "status": "pass",
            "assertion": "node_property",
            "node": node_path,
            "property": property_name,
            "value": actual,
        }
    except Exception as e:
        return {"status": "error", "assertion": "node_property", "message": str(e)}


def simulate_input_sequence(
    actions: list[dict],
    delay_ms: int = 100,
) -> dict:
    """Simula uma sequência de inputs no jogo em execução.

    Args:
        actions: Lista de ações. Cada ação tem:
            - type: "key" (tecla), "mouse" (botão), "wait" (espera).
            - key: Código da tecla (ex: 32=espaço, 87=W, 65=A).
            - pressed: True para pressionar, False para soltar.
            - duration_ms: Duração do pressionamento.
        delay_ms: Delay entre ações em ms.

    Returns:
        dict com resultado da sequência.
    """
    from tools.runtime_ops import inject_input_event

    results = []
    errors = []

    for i, action in enumerate(actions):
        action_type = action.get("type", "key")

        if action_type == "wait":
            wait_ms = action.get("duration_ms", delay_ms)
            time.sleep(wait_ms / 1000.0)
            results.append({"index": i, "action": "wait", "duration_ms": wait_ms, "status": "ok"})
            continue

        try:
            if action_type == "key":
                result = inject_input_event("key", {
                    "keycode": action["key"],
                    "pressed": action.get("pressed", True),
                })
                if action.get("pressed", True) and action.get("duration_ms"):
                    time.sleep(action["duration_ms"] / 1000.0)
                    inject_input_event("key", {"keycode": action["key"], "pressed": False})

            elif action_type == "mouse":
                result = inject_input_event("mouse_button", {
                    "button": action.get("button", 1),
                    "pressed": action.get("pressed", True),
                    "x": action.get("x", 0),
                    "y": action.get("y", 0),
                })
            else:
                errors.append({"index": i, "error": f"Tipo desconhecido: {action_type}"})
                continue

            results.append({
                "index": i,
                "action": action_type,
                "status": "ok" if result.get("status") == "success" else "injected",
                "key": action.get("key"),
            })

            time.sleep(delay_ms / 1000.0)

        except Exception as e:
            errors.append({"index": i, "action": action_type, "error": str(e)})

    return {
        "status": "success" if not errors else "partial",
        "total_actions": len(actions),
        "completed": len(results),
        "errors": errors or None,
        "results": results,
        "note": "Requere jogo em execução com GameBridge autoload",
    }
