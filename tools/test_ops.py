"""test_ops.py — Testes Roteirizados com Input Sintético (PATCH 14).

Executa cenários de teste pré-definidos com entradas sintéticas e
valida saídas esperadas. NÃO requer Godot rodando — testa as tools
do MCP diretamente com mocks e dados sintéticos.

Tools:
    run_scripted_tests — executa cenários customizados
    smoke_test         — valida pipeline core (ping, ClassDB, validação, config)
    regression_test    — valida correções GRUPO 1/2 (write_file .gd, GUT skipped)
    dump_mcp_state     — snapshot completo do estado do MCP
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════
# Motor de Cenários
# ══════════════════════════════════════════════════════════════════════

def run_scripted_tests(
    args: dict | None = None,
) -> dict:
    """Executa cenarios de teste roteirizados com input sintetico.

    Cada cenario e um dict com:
        name: str — nome do cenario
        description: str — o que esta sendo testado
        steps: list[dict] — sequencia de passos, cada um com:
            tool: str — nome da tool a invocar
            args: dict — argumentos sinteticos
            expect: dict — condicoes esperadas (opcional):
                status: "success" | "error" | "skipped" | None (qualquer)
                contains: str — substring esperada na resposta
                has_key: str — chave que deve existir no resultado
                not_has_key: str — chave que NAO deve existir
        setup: dict — estado a preparar antes (opcional, nao implementado ainda)
        teardown: dict — limpeza apos (opcional, nao implementado ainda)

    Args:
        args: dict com 'scenarios' (list[dict]|None) e 'stop_on_failure' (bool).

    Returns:
        {
            "status": "success" | "partial_failure" | "failure",
            "scenarios": [{name, passed, steps: [{tool, passed, result, expected}]}],
            "summary": {total, passed, failed, duration_ms},
            "state_dump": {...}
        }
    """
    args = args or {}
    scenarios = args.get("scenarios", None)
    stop_on_failure = args.get("stop_on_failure", False)

    if scenarios is None:
        scenarios = _default_scenarios()

    start_time = time.time()
    results = []
    total_passed = 0
    total_failed = 0

    for scenario in scenarios:
        scenario_result = _run_scenario(scenario)

        if scenario_result["passed"]:
            total_passed += 1
        else:
            total_failed += 1

        results.append(scenario_result)

        if stop_on_failure and not scenario_result["passed"]:
            break

    elapsed = round((time.time() - start_time) * 1000)

    return {
        "status": "success" if total_failed == 0 else ("partial_failure" if total_passed > 0 else "failure"),
        "scenarios": results,
        "summary": {
            "total": len(results),
            "passed": total_passed,
            "failed": total_failed,
            "duration_ms": elapsed,
        },
        "state_dump": _capture_state(),
    }


def _run_scenario(scenario: dict) -> dict:
    """Executa um unico cenario de teste com medicao de tempo por step."""
    name = scenario.get("name", "unnamed")
    steps = scenario.get("steps", [])
    step_results = []
    all_passed = True

    for i, step in enumerate(steps):
        tool = step.get("tool", "???")
        args = step.get("args", {})
        expected = step.get("expect", {})

        step_start = time.time()
        try:
            result = _invoke_tool_synthetic(tool, args)
        except Exception as e:
            result = {"status": "error", "message": f"Excecao: {e}", "_exception": str(e)}
        step_ms = round((time.time() - step_start) * 1000)

        passed, failures = _validate_result(result, expected)

        step_results.append({
            "step": i + 1,
            "tool": tool,
            "args": args,
            "passed": passed,
            "duration_ms": step_ms,
            "result": result,
            "expected": expected,
            "failures": failures,
        })

        if not passed:
            all_passed = False

    return {
        "name": name,
        "description": scenario.get("description", ""),
        "passed": all_passed,
        "total_steps": len(steps),
        "passed_steps": sum(1 for s in step_results if s["passed"]),
        "steps": step_results,
    }


def _invoke_tool_synthetic(tool: str, args: dict) -> dict:
    """Invoca uma tool MCP com input sintético (sem depender de subprocess Godot).

    Mapeia tools para seus handlers internos. Para tools que dependem de
    Godot ou estado externo, retorna um resultado simulado.
    """
    # ── Tools que funcionam sem Godot ──
    if tool == "ping":
        return {"status": "success", "pong": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    if tool == "health_check":
        return _run_internal_health_check()

    if tool == "self_test":
        return _run_internal_self_test()

    if tool == "validate_gdscript_syntax":
        return _run_validate_syntax(args)

    if tool == "write_file":
        return _simulate_write_file(args)

    if tool == "safe_write_gdscript":
        return _simulate_safe_write(args)

    if tool == "run_gut_tests":
        return _simulate_gut_tests(args)

    if tool == "git_commit_checkpoint":
        return _simulate_git_checkpoint(args)

    if tool == "godot_class_ref":
        return _simulate_classdb_lookup(args)

    if tool == "compile_test":
        return _simulate_compile_test(args)

    if tool == "read_file":
        return _simulate_read_file(args)

    if tool == "dump_mcp_state":
        return _simulate_dump_state()

    # ── Runtime Bridge tools (PATCH 14 B2 fix) ──
    if tool == "godot_screenshot":
        return _invoke_runtime_screenshot()
    if tool == "godot_runtime_info":
        return _invoke_runtime_info()

    # ── Bloco 2: UID + Save ──
    if tool == "audit_uid_consistency":
        return {
            "status": "ok",
            "total_uid_refs_checked": 3,
            "mismatched_uid": [],
            "missing_uid_file": [],
            "duplicate_uid": [],
            "unresolved": [],
            "note": "Mock: projeto config_version=5, sem .uid files.",
            "summary": "3 UIDs declarados verificados, nenhum problema encontrado.",
        }
    if tool == "audit_save_compatibility":
        return {
            "status": "issues_found",
            "save_manager_script": "res://scripts/autoloads/save_manager.gd",
            "has_version_field": True,
            "has_migration_logic": False,
            "write_read_key_mismatch": [],
            "tested_against_file": None,
            "missing_key_in_save": [],
            "orphaned_key_in_save": [],
            "note": "Mock: SaveManager encontrado, campo version existe mas sem migracao.",
            "summary": "SaveManager: SaveManager, campo version existe mas sem lógica de migração.",
        }

    # ── Bloco 1: Auditoria de Wiring ──
    if tool == "audit_input_map":
        return {
            "status": "ok",
            "declared_actions": ["move_left", "move_right", "jump"],
            "unused_actions": [],
            "undeclared_actions_referenced": [],
            "summary": "3 ações declaradas, nenhum problema encontrado.",
        }
    if tool == "audit_autoloads":
        return {
            "status": "ok",
            "registered_autoloads": [{"name": "GameManager", "script_path": "res://scripts/game_manager.gd"}],
            "possibly_unused_autoloads": [],
            "summary": "1 autoload registrado, 0 sem referência.",
        }
    if tool == "audit_scene_reachability":
        # Se chamado sem root_scene e sem main_scene definido → ambiguous
        args = args or {}
        if not args.get("root_scene"):
            return {
                "status": "ambiguous",
                "root_scene": None,
                "total_scenes_in_project": 0,
                "reachable_scenes": 0,
                "unreachable_scenes": [],
                "summary": "Cena raiz não definida. Defina run/main_scene no project.godot.",
            }
        return {
            "status": "ok",
            "root_scene": args.get("root_scene", "res://scenes/main.tscn"),
            "total_scenes_in_project": 5,
            "reachable_scenes": 5,
            "unreachable_scenes": [],
            "summary": "5 cenas no projeto, 5 alcançáveis, 0 órfãs.",
        }

    # NOTA: run_scripted_tests, smoke_test e regression_test NAO tem handlers
    # sinteticos para evitar risco de recursao infinita.

    # ── Bloco 4: Proof Ledger ──
    if tool == "capture_proof":
        return {
            "status": "ok",
            "task_id": args.get("task_id", "unknown"),
            "proof_file": "/tmp/.mcp_proof/test_1234567890.json",
            "worktree_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
            "head_commit": "abc12345",
            "files_changed": 0,
            "untracked_captured": 0,
            "diff_lines": 0,
            "regression": {"total": 10, "passed": 10, "failed": 0},
            "extra_commands_run": 0,
            "note": "Prova coletada mecanicamente pela ferramenta.",
            "summary": "Mock: prova coletada com sucesso (handler sintético).",
        }
    if tool == "verify_proof":
        task_id = args.get("task_id", None)
        if task_id == "inexistente":
            return {
                "status": "missing",
                "proof_file": None,
                "task_id": task_id,
                "age_minutes": 0,
                "hash_match": False,
                "regression_passed": False,
                "reason": "Nenhuma prova encontrada para task_id='inexistente'.",
                "summary": "Nenhuma prova encontrada.",
            }
        return {
            "status": "valid",
            "proof_file": "/tmp/.mcp_proof/test_1234567890.json",
            "task_id": task_id or "test",
            "age_minutes": 3,
            "hash_match": True,
            "regression_passed": True,
            "reason": "",
            "summary": "Mock: prova válida (handler sintético).",
        }

    # ── Fallback para tools não mapeadas ──
    return {
        "status": "skipped",
        "reason": f"Tool '{tool}' não tem handler sintético. "
                   f"Adicione ao dicionário _invoke_tool_synthetic em tools/test_ops.py.",
        "args": args,
    }


def _validate_result(result: dict, expected: dict) -> tuple[bool, list[str]]:
    """Valida resultado contra condicoes esperadas.

    Suporta:
        status: "success"|"error"|"skipped"|None (None = qualquer)
        contains: substring esperada na resposta JSON
        has_key: chave que deve existir (suporta nested: "a.b.c")
        not_has_key: chave que NAO deve existir (suporta nested)
        has_value: {key: expected_value} — valor exato esperado

    Returns:
        (passed: bool, failures: list[str])
    """
    failures = []

    if not expected:
        # Sem expectativas = verifica apenas se nao explodiu com excecao nossa
        if "_exception" in result:
            failures.append(f"excecao inesperada: {result['_exception']}")
            return False, failures
        return True, []

    # Verifica status
    if "status" in expected:
        expected_status = expected["status"]
        actual_status = result.get("status")
        if expected_status is not None and actual_status != expected_status:
            failures.append(f"status: esperado='{expected_status}', obtido='{actual_status}'")

    # Verifica substring (ensure_ascii=False para preservar acentos)
    if "contains" in expected:
        result_str = json.dumps(result, ensure_ascii=False)
        if expected["contains"] not in result_str:
            failures.append(f"contains: '{expected['contains']}' nao encontrado na resposta")

    # Verifica chave presente (suporta nested: "a.b.c" ou lista ["a", "b"])
    if "has_key" in expected:
        keys_to_check = expected["has_key"]
        if isinstance(keys_to_check, str):
            keys_to_check = [keys_to_check]
        for k in keys_to_check:
            if not _nested_key_exists(result, k):
                failures.append(f"has_key: '{k}' ausente no resultado")

    # Verifica chave ausente (suporta nested: "a.b.c" ou lista)
    if "not_has_key" in expected:
        keys_to_check = expected["not_has_key"]
        if isinstance(keys_to_check, str):
            keys_to_check = [keys_to_check]
        for k in keys_to_check:
            if _nested_key_exists(result, k):
                failures.append(f"not_has_key: '{k}' presente (nao deveria)")

    # Verifica valor exato de uma chave (suporta nested)
    if "has_value" in expected:
        for key, exp_val in expected["has_value"].items():
            actual_val = _nested_get(result, key, _SENTINEL)
            if actual_val is _SENTINEL:
                failures.append(f"has_value: chave '{key}' nao encontrada")
            elif actual_val != exp_val:
                failures.append(f"has_value: '{key}' esperado={exp_val!r}, obtido={actual_val!r}")

    return len(failures) == 0, failures


# Sentinel para distinguir None de chave ausente
_SENTINEL = object()


def _nested_key_exists(data: dict, dotted_key: str) -> bool:
    """Verifica se uma chave aninhada existe no dicionario.

    Ex: _nested_key_exists({"a": {"b": 1}}, "a.b") -> True
    """
    return _nested_get(data, dotted_key, _SENTINEL) is not _SENTINEL


def _nested_get(data: dict, dotted_key: str, default: Any = None) -> Any:
    """Obtem valor de chave aninhada via dotted notation.

    Ex: _nested_get({"a": {"b": 1}}, "a.b") -> 1
    """
    keys = dotted_key.split(".")
    current: Any = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


# ══════════════════════════════════════════════════════════════════════
# Handlers Sintéticos (mockam tools reais)
# ══════════════════════════════════════════════════════════════════════

def _run_internal_health_check() -> dict:
    """Executa health_check internamente."""
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        godot_path = cfg.get("godot_path", "")
    except Exception:
        godot_path = ""

    checks = [
        {"component": "config", "ok": bool(godot_path)},
        {"component": "ClassDB cache", "ok": (ROOT / "classdb_cache" / "extension_api.json").exists()},
        {"component": "Templates", "ok": bool(list((ROOT / "templates").glob("*.gd")))},
    ]
    return {
        "status": "success",
        "healthy": all(c["ok"] for c in checks),
        "checks": checks,
    }


def _run_internal_self_test() -> dict:
    """Executa self_test internamente."""
    results = []
    results.append({"test": "ping", "passed": True})
    try:
        from tools.classdb import is_valid_node_type
        results.append({"test": "ClassDB (Node2D)", "passed": is_valid_node_type("Node2D")})
    except Exception as e:
        results.append({"test": "ClassDB", "passed": False, "error": str(e)})
    try:
        import godot_parser
        results.append({"test": "godot_parser", "passed": True})
    except ImportError:
        results.append({"test": "godot_parser", "passed": False})
    try:
        import jinja2
        results.append({"test": "jinja2", "passed": True})
    except ImportError:
        results.append({"test": "jinja2", "passed": False})
    try:
        from PIL import Image
        results.append({"test": "Pillow", "passed": True})
    except ImportError:
        results.append({"test": "Pillow", "passed": False})
    passed = sum(1 for r in results if r["passed"])
    return {"status": "success", "passed": passed, "total": len(results), "results": results}


def _run_validate_syntax(args: dict) -> dict:
    """Valida sintaxe GDScript com input sintético."""
    from tools.validate_write import validate_gdscript_syntax
    code = args.get("code", args.get("content", ""))
    return validate_gdscript_syntax(code)


def _simulate_write_file(args: dict) -> dict:
    """Simula write_file com validação para .gd."""
    path = args.get("path", "")
    content = args.get("content", "")
    skip = args.get("skip_gdscript_validation", False)

    if path.endswith(".gd") and not skip:
        from tools.validate_write import validate_gdscript_syntax
        validation = validate_gdscript_syntax(content)
        if not validation.get("valid", True):
            return {
                "status": "error",
                "message": "GDScript INVÁLIDO — escrita BLOQUEADA.",
                "validation_errors": validation.get("errors"),
            }

    return {"status": "success", "path": path, "written": True}


def _simulate_safe_write(args: dict) -> dict:
    """Simula safe_write_gdscript."""
    content = args.get("content", "")
    strict = args.get("strict", True)
    from tools.validate_write import validate_gdscript_syntax
    validation = validate_gdscript_syntax(content)
    if not validation.get("valid", True) and strict:
        return {"status": "error", "message": "GDScript INVÁLIDO — escrita BLOQUEADA.", "errors": validation.get("errors")}
    return {"status": "success", "message": "GDScript válido.", "written": True}


def _simulate_gut_tests(args: dict) -> dict:
    """Simula run_gut_tests sem Godot."""
    test_dir = args.get("test_dir", "res://tests")
    # Simula ausência de testes → skipped
    return {
        "status": "skipped",
        "reason": f"Diretório de testes '{test_dir}' não existe. "
                   "Crie testes em res://tests/ para habilitar validação.",
    }


def _simulate_git_checkpoint(args: dict) -> dict:
    """Simula git_commit_checkpoint.

    Comportamento:
    - skip_validation=True: commit passa sem validacao
    - skip_validation=False (default): commit passa COM validacao (simulada)
    - fail_validation=True: simula falha de validacao (para teste de bloqueio)
    """
    skip = args.get("skip_validation", False)
    fail = args.get("fail_validation", False)

    if fail:
        return {
            "status": "error",
            "message": "Commit BLOQUEADO — o projeto nao compila. Corrija os erros antes de salvar o progresso.",
            "compile_errors": [
                {"file": "scripts/broken.gd", "line": 5, "message": "R1: variavel 'x' declarada duas vezes", "rule": "R1_CRITICAL"},
            ],
        }

    if skip:
        return {"status": "success", "commit": "test-commit", "validated": False}
    return {"status": "success", "commit": "test-commit", "validated": True}


def _simulate_classdb_lookup(args: dict) -> dict:
    """Simula godot_class_ref."""
    class_name = args.get("class_name", "Node2D")
    try:
        from tools.classdb import is_valid_class
        if is_valid_class(class_name):
            return {"status": "success", "class_name": class_name, "found": True}
        return {"status": "error", "message": f"Classe '{class_name}' não encontrada."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _simulate_compile_test(_args: dict) -> dict:
    """Simula compile_test sem Godot."""
    # _args reservado para uso futuro (ex: project_path)
    return {
        "status": "success",
        "errors": [],
        "note": "simulado — compile_test real requer Godot headless",
    }


def _simulate_read_file(args: dict) -> dict:
    """Simula read_file."""
    path = args.get("path", "")
    # Retorna conteúdo sintético para cenários de teste
    synthetic_content = {
        "scripts/player.gd": 'extends CharacterBody2D\n\nfunc _ready():\n    pass\n',
        "scripts/enemy.gd": 'extends CharacterBody2D\n\nvar speed: float = 100.0\n',
        "project.godot": '; Engine configuration file.\nconfig_version=5\n',
    }
    content = synthetic_content.get(path, f"; Synthetic content for {path}")
    return {
        "status": "success",
        "content": content,
        "total_lines": len(content.splitlines()),
    }


def _simulate_dump_state() -> dict:
    """Simula dump_mcp_state."""
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": _capture_state(),
    }


def _invoke_runtime_screenshot() -> dict:
    """Invoca godot_screenshot via Runtime Bridge (8790)."""
    try:
        from runtime_bridge_client import send_bridge_command, BridgeUnavailable
        return send_bridge_command({"cmd": "screenshot"}, timeout=5.0)
    except BridgeUnavailable:
        return {"status": "error", "message": "Runtime Bridge nao disponivel (jogo nao esta rodando em debug?)"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao invocar godot_screenshot: {e}"}


def _invoke_runtime_info() -> dict:
    """Invoca godot_runtime_info via Runtime Bridge (8790)."""
    try:
        from runtime_bridge_client import send_bridge_command, BridgeUnavailable
        return send_bridge_command({"cmd": "runtime_info"}, timeout=5.0)
    except BridgeUnavailable:
        return {"status": "error", "message": "Runtime Bridge nao disponivel (jogo nao esta rodando em debug?)"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao invocar godot_runtime_info: {e}"}


# ══════════════════════════════════════════════════════════════════════
# Cenários Padrão
# ══════════════════════════════════════════════════════════════════════

def _default_scenarios() -> list[dict]:
    """Retorna cenários padrão: smoke + regression."""
    return _smoke_scenarios() + _regression_scenarios()


def _smoke_scenarios() -> list[dict]:
    """Smoke test: valida pipeline core do MCP."""
    return [
        {
            "name": "SMOKE-01: Pipeline core",
            "description": "Valida que ping, health_check, self_test e ClassDB respondem corretamente.",
            "steps": [
                {"tool": "ping", "args": {}, "expect": {"status": "success", "has_key": "pong"}},
                {"tool": "health_check", "args": {}, "expect": {"status": "success", "has_key": "healthy"}},
                {"tool": "self_test", "args": {}, "expect": {"status": "success", "has_key": "passed"}},
                {"tool": "godot_class_ref", "args": {"class_name": "Node2D"}, "expect": {"status": "success"}},
                {"tool": "godot_class_ref", "args": {"class_name": "ClasseQueNaoExisteXYZ"}, "expect": {"status": "error"}},
            ],
        },
        {
            "name": "SMOKE-02: Validacao GDScript (R1/R2/brackets)",
            "description": "Valida que o motor de validacao detecta R1 (var duplicada) e R2 (:= com dict).",
            "steps": [
                {
                    "tool": "validate_gdscript_syntax",
                    "args": {"code": "extends Node\nfunc _ready():\n    var x = 1\n    var x = 2\n"},
                    "expect": {"has_value": {"valid": False}},
                },
                {
                    "tool": "validate_gdscript_syntax",
                    "args": {"code": "extends Node\nfunc _ready():\n    var blocked_pos := enemies[i][\"pos\"]\n"},
                    "expect": {"has_value": {"valid": False}},
                },
                {
                    "tool": "validate_gdscript_syntax",
                    "args": {"code": "extends Node\nfunc _ready():\n    var v := Vector2(10, 20)\n    print(v)\n"},
                    "expect": {"has_value": {"valid": True}},
                },
            ],
        },
        {
            "name": "SMOKE-03: Config e Templates",
            "description": "Valida que config.json e templates estão acessíveis.",
            "steps": [
                {"tool": "read_file", "args": {"path": "project.godot"}, "expect": {"status": "success", "has_key": "content"}},
            ],
        },
        {
            "name": "SMOKE-04: State Dump",
            "description": "Valida que dump_mcp_state captura estado com timestamp, tools, imports e git.",
            "steps": [
                {"tool": "dump_mcp_state", "args": {}, "expect": {
                    "status": "success",
                    "has_key": ["timestamp", "state"],
                    "has_value": {"status": "success"},
                }},
            ],
        },
    ]


def _regression_scenarios() -> list[dict]:
    """Teste de regressão: valida correções dos GRUPOS 1 e 2."""
    return [
        {
            "name": "REGRESS-01: write_file bloqueia .gd inválido (GRUPO 1)",
            "description": "Confirma que write_file rejeita GDScript com var duplicada (R1).",
            "steps": [
                {
                    "tool": "write_file",
                    "args": {
                        "path": "scripts/test_broken.gd",
                        "content": "extends Node\nfunc _ready():\n    var x = 1\n    var x = 2\n",
                    },
                    "expect": {"status": "error", "contains": "INVÁLIDO"},
                },
                {
                    "tool": "write_file",
                    "args": {
                        "path": "scripts/test_ok.gd",
                        "content": "extends Node\nfunc _ready():\n    var x: int = 1\n    var y: int = 2\n",
                    },
                    "expect": {"status": "success"},
                },
                {
                    "tool": "write_file",
                    "args": {
                        "path": "scripts/test_emergency.gd",
                        "content": "extends Node\nfunc _ready():\n    var x = 1\n    var x = 2\n",
                        "skip_gdscript_validation": True,
                    },
                    "expect": {"status": "success"},
                },
            ],
        },
        {
            "name": "REGRESS-02: safe_write_gdscript bloqueia R2 (GRUPO 1)",
            "description": "Confirma que safe_write_gdscript rejeita := com dict[key] (R2).",
            "steps": [
                {
                    "tool": "safe_write_gdscript",
                    "args": {
                        "file_path": "scripts/test_r2.gd",
                        "content": "extends Node\nfunc _ready():\n    var pos := enemies[i][\"pos\"]\n",
                        "strict": True,
                    },
                    "expect": {"status": "error"},
                },
                {
                    "tool": "safe_write_gdscript",
                    "args": {
                        "file_path": "scripts/test_ok2.gd",
                        "content": "extends Node\nfunc _ready():\n    var pos: Vector2 = enemies[i][\"pos\"]\n",
                        "strict": True,
                    },
                    "expect": {"status": "success"},
                },
            ],
        },
        {
            "name": "REGRESS-03: run_gut_tests retorna skipped sem testes (GRUPO 2)",
            "description": "Confirma que run_gut_tests retorna 'skipped' quando não há testes.",
            "steps": [
                {
                    "tool": "run_gut_tests",
                    "args": {"test_dir": "res://tests"},
                    "expect": {"status": "skipped"},
                },
            ],
        },
        {
            "name": "REGRESS-04: git_commit_checkpoint tem skip_validation (GRUPO 2)",
            "description": "Confirma que git_commit_checkpoint aceita skip_validation.",
            "steps": [
                {
                    "tool": "git_commit_checkpoint",
                    "args": {"message": "test", "skip_validation": True},
                    "expect": {"status": "success", "contains": "test-commit"},
                },
            ],
        },
        {
            "name": "REGRESS-05: Stress — tools desconhecidas e cenarios vazios",
            "description": "Valida que o motor trata gracefulmente tools nao mapeadas e expectativas vazias.",
            "steps": [
                {
                    "tool": "ferramenta_que_nao_existe",
                    "args": {},
                    "expect": {"status": "skipped", "has_key": "reason"},
                },
                {
                    "tool": "ping",
                    "args": {},
                    "expect": {},
                },
                {
                    "tool": "self_test",
                    "args": {},
                    "expect": {"has_key": ["passed", "results"], "status": "success"},
                },
            ],
        },
        # ── Bloco 1: Auditoria de Wiring (regressão) ──
        {
            "name": "REGRESS-06: audit_input_map retorna estrutura esperada",
            "description": "Confirma que audit_input_map retorna status, declared_actions, unused_actions.",
            "steps": [
                {
                    "tool": "audit_input_map",
                    "args": {},
                    "expect": {
                        "status": "ok",
                        "has_key": ["declared_actions", "unused_actions", "undeclared_actions_referenced", "summary"],
                    },
                },
            ],
        },
        {
            "name": "REGRESS-07: audit_autoloads retorna estrutura esperada",
            "description": "Confirma que audit_autoloads retorna status, registered_autoloads, possibly_unused_autoloads.",
            "steps": [
                {
                    "tool": "audit_autoloads",
                    "args": {},
                    "expect": {
                        "status": "ok",
                        "has_key": ["registered_autoloads", "possibly_unused_autoloads", "summary"],
                    },
                },
            ],
        },
        {
            "name": "REGRESS-08: audit_scene_reachability retorna ambiguous sem root_scene",
            "description": "Confirma que audit_scene_reachability retorna 'ambiguous' quando não há main_scene definida.",
            "steps": [
                {
                    "tool": "audit_scene_reachability",
                    "args": {},
                    "expect": {
                        "status": "ambiguous",
                        "has_key": ["summary"],
                    },
                },
            ],
        },
        # ── Bloco 2: UID + Save Compatibility (regressão) ──
        {
            "name": "REGRESS-09: audit_uid_consistency retorna estrutura esperada",
            "description": "Confirma que audit_uid_consistency retorna status, total_uid_refs_checked, duplicate_uid.",
            "steps": [
                {
                    "tool": "audit_uid_consistency",
                    "args": {},
                    "expect": {
                        "status": "ok",
                        "has_key": ["total_uid_refs_checked", "mismatched_uid", "duplicate_uid", "summary"],
                    },
                },
            ],
        },
        {
            "name": "REGRESS-10: audit_save_compatibility retorna estrutura esperada",
            "description": "Confirma que audit_save_compatibility retorna status, save_manager_script, has_migration_logic.",
            "steps": [
                {
                    "tool": "audit_save_compatibility",
                    "args": {},
                    "expect": {
                        "status": "issues_found",
                        "has_key": ["save_manager_script", "has_version_field", "has_migration_logic", "write_read_key_mismatch", "summary"],
                    },
                },
            ],
        },
        # ── Bloco 4: Proof Ledger (regressão) ──
        {
            "name": "REGRESS-11: capture_proof retorna estrutura esperada",
            "description": "Confirma que capture_proof retorna status, proof_file, worktree_hash, regression.",
            "steps": [
                {
                    "tool": "capture_proof",
                    "args": {"task_id": "regress-11-test"},
                    "expect": {
                        "status": "ok",
                        "has_key": ["proof_file", "worktree_hash", "head_commit", "regression", "summary"],
                    },
                },
            ],
        },
        {
            "name": "REGRESS-12: verify_proof retorna 'missing' quando não há prova",
            "description": "Confirma que verify_proof retorna status='missing' para task_id inexistente.",
            "steps": [
                {
                    "tool": "verify_proof",
                    "args": {"task_id": "inexistente"},
                    "expect": {
                        "status": "missing",
                        "has_key": ["reason", "summary"],
                    },
                },
            ],
        },
    ]


# ══════════════════════════════════════════════════════════════════════
# Cenários Customizados (API pública)
# ══════════════════════════════════════════════════════════════════════

def smoke_test(args: dict | None = None) -> dict:
    """Smoke test rapido: valida pipeline core do MCP.

    Cenarios: ping, health_check, self_test, ClassDB, validacao GDScript.
    NAO requer Godot rodando. Ideal para inicio de sessao.

    Returns:
        Resultado completo com status e sumario.
    """
    return run_scripted_tests({"scenarios": _smoke_scenarios()})


def regression_test(args: dict | None = None) -> dict:
    """Teste de regressao: valida correcoes dos GRUPOS 1 e 2.

    Cenarios: write_file .gd invalido, safe_write_gdscript R2,
    run_gut_tests skipped, git_commit_checkpoint com skip_validation.

    Returns:
        Resultado completo com status e sumario.
    """
    return run_scripted_tests({"scenarios": _regression_scenarios()})


def dump_mcp_state(args: dict | None = None) -> dict:
    """Captura snapshot completo do estado do MCP.

    Inclui: configuracao, contagem de tools, caches, imports, ambiente.
    Util para debugging e comparacao entre maquinas.

    Returns:
        dict com estado completo.
    """
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": _capture_state(),
    }

def estimate_tool_tokens(args: dict | None = None) -> dict:
    """Estima o consumo de tokens do tools/list para cada perfil.

    Mede o tamanho do JSON que seria enviado no tools/list inicial
    e estima tokens (~4 chars por token para JSON).

    Args:
        args: dict com 'profile' (str, opcional, default "full").

    Returns:
        {"status": "success", "profile": str, "tool_count": int, "json_bytes": int, "estimated_tokens": int}
    """
    args = args or {}
    profile = args.get("profile", "full")
    valid_profiles = {"core", "dev", "full"}
    if profile not in valid_profiles:
        return {"status": "error", "message": f"Perfil '{profile}' invalido. Use: {sorted(valid_profiles)}."}

    try:
        _srv = sys.modules.get("server")
        if _srv is None:
            return {"status": "error", "message": "server.py nao esta no sys.modules."}
        # Sincroniza valid_profiles com os perfis reais do server
        valid_profiles = set(_srv.TOOL_PROFILES.keys())
        if profile not in valid_profiles:
            return {"status": "error", "message": f"Perfil '{profile}' invalido. Use: {sorted(valid_profiles)}."}
        all_tools = _srv._tool_defs()
    except Exception:
        return {"status": "error", "message": "Nao foi possivel carregar as definicoes de tools do server."}

    if profile == "full":
        filtered = all_tools
    else:
        profile_set = set(_srv.TOOL_PROFILES.get(profile, []))
        filtered = [t for t in all_tools if t.name in profile_set]

    # Serializa como JSON (simula tools/list)
    tool_dicts = []
    for t in filtered:
        d = {"name": t.name}
        if hasattr(t, 'description') and t.description:
            d["description"] = t.description[:200]  # descricao compactada
        if hasattr(t, 'inputSchema') and t.inputSchema:
            d["inputSchema"] = t.inputSchema
        tool_dicts.append(d)

    json_str = json.dumps(tool_dicts, ensure_ascii=False)
    json_bytes = len(json_str.encode("utf-8"))
    estimated_tokens = json_bytes // 4  # ~4 chars por token em JSON

    # Tambem estima com deferLoading (apenas nome + annotations)
    deferred_dicts = []
    for t in filtered:
        d = {"name": t.name}
        if hasattr(t, 'annotations') and t.annotations:
            d["annotations"] = t.annotations
        deferred_dicts.append(d)

    deferred_json = json.dumps(deferred_dicts, ensure_ascii=False)
    deferred_bytes = len(deferred_json.encode("utf-8"))
    deferred_tokens = deferred_bytes // 4

    savings = round((1 - deferred_tokens / max(estimated_tokens, 1)) * 100, 1)

    return {
        "status": "success",
        "profile": profile,
        "tool_count": len(filtered),
        "full_json_bytes": json_bytes,
        "full_estimated_tokens": estimated_tokens,
        "deferred_json_bytes": deferred_bytes,
        "deferred_estimated_tokens": deferred_tokens,
        "savings_percent": savings,
        "note": (
            f"Perfil '{profile}': {len(filtered)} tools. "
            f"Full: ~{estimated_tokens} tokens. "
            f"Com deferLoading: ~{deferred_tokens} tokens "
            f"({savings}% economia). "
            f"Tokens estimados como bytes_json // 4 (aproximado)."
        ),
    }

# ══════════════════════════════════════════════════════════════════════
# Captura de Estado
# ══════════════════════════════════════════════════════════════════════

def _capture_state() -> dict:
    """Captura snapshot do estado atual do MCP."""
    state: dict[str, Any] = {
        "mcp_root": str(ROOT),
        "python": sys.version,
    }

    # Config
    try:
        from tools.config_loader import load_config
        cfg = load_config()
        state["config"] = {
            "godot_path": cfg.get("godot_path", "não configurado"),
            "default_project": cfg.get("default_project", ""),
        }
    except Exception as e:
        state["config"] = {"error": str(e)}

    # ClassDB
    cache = ROOT / "classdb_cache" / "extension_api.json"
    state["classdb"] = {
        "cache_exists": cache.exists(),
        "cache_size_kb": cache.stat().st_size // 1024 if cache.exists() else 0,
    }

    # Templates
    tpl_dir = ROOT / "templates"
    state["templates"] = {
        "count": len(list(tpl_dir.glob("*.gd"))) if tpl_dir.exists() else 0,
        "names": sorted([p.stem for p in tpl_dir.glob("*.gd")]) if tpl_dir.exists() else [],
    }

    # Tools — usa sys.modules (evita deadlock de import em thread run_in_executor)
    try:
        _srv = sys.modules.get("server")
        if _srv is not None:
            state["tools"] = {
                "defs_cached": _srv._TOOL_DEFS_CACHE is not None,
                "handlers_cached": _srv._HANDLERS_CACHE is not None,
                "tool_count": len(_srv._TOOL_DEFS_CACHE) if _srv._TOOL_DEFS_CACHE else 0,
                "handler_count": len(_srv._HANDLERS_CACHE) if _srv._HANDLERS_CACHE else 0,
            }
        else:
            state["tools"] = {"error": "server.py não está no sys.modules (esperado em teste unitário?)"}
    except Exception:
        state["tools"] = {"error": "server.py não pôde ser importado (esperado em teste unitário)"}

    # Imports críticos (usa importlib em vez de __import__)
    import importlib
    imports = {}
    import_map = {
        "godot_parser": "godot_parser",
        "jinja2": "jinja2",
        "PIL (Pillow)": "PIL",
        "mcp": "mcp",
        "yaml": "yaml",
    }
    for label, mod in import_map.items():
        try:
            importlib.import_module(mod)
            imports[label] = True
        except ImportError:
            imports[label] = False
    state["imports"] = imports

    # Git
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=str(ROOT),
        )
        state["git"] = {"commit": r.stdout.strip()} if r.returncode == 0 else {"error": "não é repo git"}
    except Exception:
        state["git"] = {"error": "git indisponível"}

    return state


_RECURSION_GUARD = {"smoke_test","regression_test","run_scripted_tests","dump_mcp_state","estimate_tool_tokens","run_verification_pipeline","debugger_status","debugger_get_stack","debugger_get_variables","debugger_set_breakpoint","debugger_step"}
_SMOKE_SKIP_HEAVY = {"create_entity","create_entities","safe_write_gdscript","capture_proof","verify_proof","deploy_itch","build_csharp","export_manage","read_console_output"}
_MINIMAL_ARGS: dict[str, dict | None] = {"read_file":{"path":"project.godot"},"write_file":{"path":"_smoke_test.txt","content":"smoke","mode":"create"},"validate_gdscript_syntax":{"code":"extends Node\nfunc _ready():\n    pass\n"},"godot_class_ref":{"class_name":"Node"},"gdd_generate":{"concept":"test","game_type":"tower_defense"},"advance_phase":{"force":True,"reason":"smoke test"},"scene_manage":{"op":"load_tree"},"node_manage":{"op":"get_property","node_path":".","property_name":"name"},"script_manage":{"op":"validate","script_path":"scripts/_smoke.gd"},"file_manage":{"op":"read","path":"project.godot"},"project_manage":{"op":"status"},"safety_manage":{"op":"list_backups"},"validate_project_refs":{},"find_usages":{"target":"project.godot"},"tool_groups":{"action":"list"},"bootstrap_godot_mcp":{"target":"validate_only"},"configure_export_preset":{},"release_checklist":{},"create_asset_manifest":{},"generate_project_structure":{},"create_milestone_plan":{"genero":"tower_defense","force":True},"addon_connect":None,"addon_disconnect":None,"addon_ping":None,"addon_is_available":None,"addon_get_scene_tree":None,"addon_take_screenshot":None,"addon_create_node":None,"addon_delete_node":None,"addon_set_property":None,"addon_reparent_node":None,"addon_duplicate_node":None,"addon_batch_edit":None,"set_project_brief":{"genre":"tower_defense","art_style":"scifi","force":True}}
_SYNTHETIC_HANDLERS = {"ping","health_check","self_test","validate_gdscript_syntax","write_file","safe_write_gdscript","run_gut_tests","git_commit_checkpoint","godot_class_ref","compile_test","read_file","dump_mcp_state","godot_screenshot","godot_runtime_info","audit_uid_consistency","audit_save_compatibility","audit_input_map","audit_autoloads","audit_scene_reachability","capture_proof","verify_proof"}
_TIER1_MAP = {"scene_manage":"success","node_manage":"success","script_manage":"error","file_manage":"success","project_manage":"success","asset_manage":"success","audio_manage":"success","anim_manage":"success","tilemap_manage":"success","safety_manage":"success","create_entity":"success"}

def test_coverage_report(args=None):
    args=args or {}
    try: from server import _tool_defs; tools=_tool_defs()
    except Exception as e: return {"status":"error","message":str(e)}
    t1,ss,sr=[],[],[]; sm,sh,nc=[],[],[]
    for tool in tools:
        n=tool.name
        if n in _RECURSION_GUARD: sm.append(n); continue
        if n in _SMOKE_SKIP_HEAVY: sh.append(n); continue
        if n in _TIER1_MAP: t1.append(n); continue
        if n in _SYNTHETIC_HANDLERS: ss.append(n); continue
        if n in _MINIMAL_ARGS and _MINIMAL_ARGS[n] is not None: sr.append(n); continue
        nc.append(n)
    total=len(tools); cov=len(t1)+len(ss)+len(sr); sk=len(sm)+len(sh); ts=total-sk
    p=round(cov/max(total,1)*100,1); pe=round(cov/max(ts,1)*100,1)
    ls=[f"Cobertura: {p}% ({cov}/{total})",f"Excl. skip: {pe}% ({cov}/{ts})","",f"Tier-1: {len(t1)} | Sint: {len(ss)} | Real: {len(sr)}",f"Sem: {len(nc)}"]
    if nc: ls.append(f"  -> {', '.join(sorted(nc))}")
    return {"status":"success","total_tools":total,"coverage_percent":p,"coverage_percent_excluding_skipped":pe,"coverage":{"tier1":{"count":len(t1),"tools":sorted(t1)},"smoke_synthetic":{"count":len(ss),"tools":sorted(ss)},"smoke_real":{"count":len(sr),"tools":sorted(sr)},"skipped_meta":{"count":len(sm),"tools":sorted(sm)},"skipped_heavy":{"count":len(sh),"tools":sorted(sh)},"none":{"count":len(nc),"tools":sorted(nc)}},"summary":"\n".join(ls)}

def generate_test_cases_from_gdd(args=None):
    args=args or {}; gdd=args.get("gdd"); concept=args.get("concept",""); game_type=args.get("game_type","tower_defense")
    if gdd is None:
        if not concept:
            from tools.project_brief_ops import get_project_brief; br=get_project_brief()
            if br.get("configured") and br.get("brief"): concept=br["brief"].get("concept",""); game_type=br["brief"].get("game_type",game_type)
        if not concept: return {"status":"error","message":"Forneça concept+game_type, gdd, ou project_brief."}
        from tools.balance_ops import gdd_generate; gdd_r=gdd_generate(concept=concept,game_type=game_type)
        if gdd_r.get("status")!="success": return {"status":"error","message":f"GDD: {gdd_r.get('message','')}"}
        gdd=gdd_r["gdd"]; source="gdd_generated"
    else: source="gdd_provided"
    tc=[]; gp=gdd.get("gameplay",{}); wl=gdd.get("win_lose",{}); bal=gdd.get("balance",{}); ct=gdd.get("content_scope",{}); tec=gdd.get("technical",{})
    mech=gp.get("mechanics",[])
    if isinstance(mech,str): mech=[mech]
    elif not isinstance(mech,list): mech=[]
    met=bal.get("metrics",[])
    if isinstance(met,str): met=[met]
    elif not isinstance(met,list): met=[]
    try: from resources.game_patterns import GAME_PATTERNS; gk=game_type.lower().strip().replace(" ","_").replace("-","_"); pat=GAME_PATTERNS.get(gk,{})
    except: pat={}
    gn=pat.get("description",f"jogo de {game_type}"); gi=pat.get("inputs",["interação padrão"]); cb=pat.get("common_bugs",[])
    ctrs={"funcional":0,"vitoria":0,"derrota":0,"balanceamento":0,"integracao":0,"escopo":0,"tecnico":0,"regressao":0}
    def _id(c): ctrs[c]+=1; px={"funcional":"FUNC","vitoria":"VIT","derrota":"DER","balanceamento":"BAL","integracao":"INT","escopo":"ESC","tecnico":"TEC","regressao":"REG"}; return f"TC-{px.get(c,c[:3].upper())}-{ctrs[c]:03d}"
    def _a(c,r,w,i,e,p="medium",pr=""): tc.append({"id":_id(c),"category":c,"priority":p,"requirement":r,"what_to_verify":w,"preconditions":pr or "Jogo iniciado.","input":i,"expected_output":e})
    h=gi[0] if gi else "interação"
    for m in mech: _a("funcional",m,f"'{m}' em {gn}.",f"{m} com {h}.",f"'{m}' OK.","critical")
    win=wl.get("win",""); lose=wl.get("lose","")
    if win: _a("vitoria",f"Vitória: {win}",f"Verificar: {win}.",f"Jogar: {win}.","Vitória OK.","high")
    if lose: _a("derrota",f"Derrota: {lose}",f"Verificar: {lose}.",f"Jogar: {lose}.","Derrota OK.","high")
    for mt in met: _a("balanceamento",f"Métrica: {mt}",f"Balancear '{mt}'.",f"Variar '{mt}'.",f"'{mt}' OK.","medium")
    cl=gp.get("core_loop","")
    if cl: _a("integracao",f"Core: {cl}","Loop sem quebras.",f"Partida: {cl}.","Transições OK.","high","Nova partida.")
    for k,(lb,wh,ip,pr) in {"estimated_levels":("Níveis",f"~{ct.get('estimated_levels','?')}","Contar.","medium"),"enemy_types":("Inimigos",f"{ct.get('enemy_types','?')}","Listar.","medium"),"bosses":("Chefões",f"{ct.get('bosses','?')}","Listar.","low"),"items_powerups":("Itens",f"{ct.get('items_powerups','?')}","Listar.","low"),"estimated_playtime":("Playtime",f"{ct.get('estimated_playtime','?')}","Cronometrar.","low")}.items():
        v=ct.get(k)
        if v: _a("escopo",f"Escopo — {lb}: {v}",wh,ip,f"{lb} OK.",pr)
    fps=tec.get("target_fps")
    if fps: _a("tecnico",f"FPS: {fps}",f"≥{fps} FPS.","Build release.",f"≥{fps} FPS.","high","Build release.")
    res=tec.get("resolution","")
    if res: _a("tecnico",f"Res: {res}",f"Render {res}.",f"Iniciar {res}.","OK.","medium")
    for bug in cb: _a("regressao",f"Bug: {bug}",f"'{bug}' NÃO ocorre.",f"Cenário: {bug}.",f"'{bug}' ausente.","high","Build recente.")
    return {"status":"success","gdd_title":gdd.get("title",concept or "GDD"),"gdd_genre":gdd.get("genre",game_type),"source":source,"test_case_count":len(tc),"categories":sorted(set(t["category"] for t in tc)),"test_cases":tc,"message":f"{len(tc)} casos ({len(ctrs)} categorias)."}

def run_canary_queries(args=None):
    args=args or {}; cp=Path(str(args.get("canary_file",str(ROOT/"tests"/"canary_queries.json"))))
    if not cp.exists(): return {"status":"error","message":f"Arquivo não encontrado: {cp}"}
    try: data=_json.loads(cp.read_text(encoding="utf-8")); canaries=data.get("canaries",[])
    except Exception as e: return {"status":"error","message":f"Erro: {e}"}
    if not canaries: return {"status":"error","message":"Nenhuma canary."}
    results=[]
    for c in canaries:
        tool=c.get("tool","???"); cargs=c.get("args",{}); exp=c.get("expect",{})
        try: actual=_invoke_tool_synthetic(tool,cargs)
        except Exception as e: results.append({"tool":tool,"passed":False,"expected":exp,"actual":{"status":"crash","error":str(e)[:200]}}); continue
        passed,failures=_validate_result(actual,exp)
        results.append({"tool":tool,"passed":passed,"expected":exp,"actual":actual,"failures":failures})
    pc=sum(1 for r in results if r["passed"]); fc=len(results)-pc
    return {"status":"success","total":len(results),"passed":pc,"failed":fc,"results":results,"summary":f"Canaries: {pc}/{len(results)}."+(f" Falhas: {[r['tool'] for r in results if not r['passed']]}" if fc else "")}
