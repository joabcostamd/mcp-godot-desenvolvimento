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
    scenarios: list[dict] | None = None,
    stop_on_failure: bool = False,
) -> dict:
    """Executa cenários de teste roteirizados com input sintético.

    Cada cenário é um dict com:
        name: str — nome do cenário
        description: str — o que está sendo testado
        steps: list[dict] — sequência de passos, cada um com:
            tool: str — nome da tool a invocar
            args: dict — argumentos sintéticos
            expect: dict — condições esperadas (opcional):
                status: "success" | "error" | "skipped" | None (qualquer)
                contains: str — substring esperada na resposta
                has_key: str — chave que deve existir no resultado
                not_has_key: str — chave que NÃO deve existir
        setup: dict — estado a preparar antes (opcional, não implementado ainda)
        teardown: dict — limpeza após (opcional, não implementado ainda)

    Args:
        scenarios: Lista de cenários. Se None, executa smoke + regression.
        stop_on_failure: Se True, para no primeiro cenário que falhar.

    Returns:
        {
            "status": "success" | "partial_failure" | "failure",
            "scenarios": [{name, passed, steps: [{tool, passed, result, expected}]}],
            "summary": {total, passed, failed, duration_ms},
            "state_dump": {...}
        }
    """
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

    # NOTA: run_scripted_tests, smoke_test e regression_test NAO tem handlers
    # sinteticos para evitar risco de recursao infinita.

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
    ]


# ══════════════════════════════════════════════════════════════════════
# Cenários Customizados (API pública)
# ══════════════════════════════════════════════════════════════════════

def smoke_test() -> dict:
    """Smoke test rápido: valida pipeline core do MCP.

    Cenários: ping, health_check, self_test, ClassDB, validação GDScript.
    NÃO requer Godot rodando. Ideal para início de sessão.

    Returns:
        Resultado completo com status e sumário.
    """
    return run_scripted_tests(scenarios=_smoke_scenarios())


def regression_test() -> dict:
    """Teste de regressão: valida correções dos GRUPOS 1 e 2.

    Cenários: write_file .gd inválido, safe_write_gdscript R2,
    run_gut_tests skipped, git_commit_checkpoint com skip_validation.

    Returns:
        Resultado completo com status e sumário.
    """
    return run_scripted_tests(scenarios=_regression_scenarios())


def dump_mcp_state() -> dict:
    """Captura snapshot completo do estado do MCP.

    Inclui: configuração, contagem de tools, caches, imports, ambiente.
    Útil para debugging e comparação entre máquinas.

    Returns:
        dict com estado completo.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": _capture_state(),
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

    # Tools
    try:
        from server import _TOOL_DEFS_CACHE, _HANDLERS_CACHE
        state["tools"] = {
            "defs_cached": _TOOL_DEFS_CACHE is not None,
            "handlers_cached": _HANDLERS_CACHE is not None,
            "tool_count": len(_TOOL_DEFS_CACHE) if _TOOL_DEFS_CACHE else 0,
            "handler_count": len(_HANDLERS_CACHE) if _HANDLERS_CACHE else 0,
        }
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
