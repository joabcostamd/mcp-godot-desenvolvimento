"""gut_ops.py — GUT Test Runner (Fase 2C / B3).

Executa GUT (Godot Unit Test) via Godot headless e retorna
resultados parseados. Inspirado no diegobr4nd/godot-gut.

Tool: run_gut_tests — executa suite de testes GUT.
"""

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_gut_tests(
    project_path: str | None = None,
    test_dir: str = "res://tests",
    godot_path: str | None = None,
    timeout: int = 60,
) -> dict:
    """Executa testes GUT no projeto Godot.

    Args:
        project_path: Caminho do projeto Godot.
        test_dir: Diretório dos testes (default: res://tests).
        godot_path: Caminho do executável Godot.
        timeout: Timeout em segundos.

    Returns:
        dict com resultados parseados.
    """
    # Detecta projeto
    if not project_path:
        try:
            from tools.project_ops import get_project_settings
            settings = get_project_settings()
            project_path = settings.get("project_path", "")
        except Exception:
            pass

    if not project_path:
        return {"status": "error", "message": "Projeto não encontrado"}

    # Detecta Godot
    if not godot_path:
        try:
            from tools.config_loader import load_config
            config = load_config()
            godot_path = config.get("godot_path", "")
        except Exception:
            pass

    if not godot_path:
        return {"status": "error", "message": "Godot não encontrado. Configure godot_path em config.json"}

    if not Path(godot_path).exists():
        return {"status": "error", "message": f"Godot executável não encontrado: {godot_path}"}

    # ── Pre-check: verifica se existem testes antes de invocar o Godot ──
    # Evita falso-positivo "tests_failed" quando na verdade não há testes configurados.
    # (GRUPO 2.3 da auditoria)
    tests_path = Path(project_path) / test_dir.replace("res://", "")
    if not tests_path.exists():
        return {
            "status": "skipped",
            "reason": f"Diretório de testes '{test_dir}' não existe. "
                       f"Crie testes em {test_dir}/ para habilitar validação.",
            "hint": "Use test_*.gd como padrão de nomenclatura (ex: test_player.gd).",
        }
    test_files = list(tests_path.glob("test_*.gd")) + list(tests_path.glob("*.gd"))
    if not test_files:
        return {
            "status": "skipped",
            "reason": f"Nenhum arquivo de teste encontrado em '{test_dir}'. "
                       f"Crie scripts de teste (ex: test_player.gd) para habilitar validação.",
        }

    # Warm-up: importa o projeto antes de rodar os testes, senão
    # class_name customizados não registram e a suíte falha por
    # motivo errado (não é um bug real do jogo).
    try:
        from tools.subprocess_utils import run_subprocess_safe
        run_subprocess_safe(
            [godot_path, "--headless", "--path", project_path, "--import", "--quit"],
            timeout=30,
        )
    except Exception:
        pass  # Se o warm-up falhar, tenta rodar os testes mesmo assim

    # Executa GUT via headless
    start = time.time()
    try:
        result = run_subprocess_safe(
            [
                godot_path,
                "--headless",
                "--path", project_path,
                "-s", "addons/gut/gut_cmdln.gd",
                "-gdir", test_dir,
                "-gexit",
                "-glog=1",
            ],
            timeout=timeout,
            cwd=project_path,
        )

        output = result.stdout + "\n" + result.stderr
        parsed = _parse_gut_output(output)

        elapsed = round((time.time() - start) * 1000)

        return {
            "status": "success" if result.returncode == 0 else "tests_failed",
            "exit_code": result.returncode,
            "duration_ms": elapsed,
            "results": parsed,
            "raw_output": output[-2000:],  # últimas 2000 chars
        }

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Timeout após {timeout}s"}
    except FileNotFoundError:
        return {"status": "error", "message": "GUT não instalado. Instale via AssetLib: GUT (Godot Unit Test)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _parse_gut_output(output: str) -> dict:
    """Parseia saída do GUT para estrutura JSON."""
    lines = output.splitlines()

    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "pending": 0,
        "errors": 0,
        "assertions": 0,
    }

    tests = []
    current_test = None

    for line in lines:
        line = line.strip()

        # Detecta início de teste
        if "-> TEST" in line or line.startswith("* "):
            if current_test:
                tests.append(current_test)
            current_test = {"name": line, "status": "unknown", "assertions": []}

        # Resultado de assertion
        elif "passing:" in line.lower() or "[PASS]" in line:
            if current_test:
                current_test["assertions"].append({"status": "pass", "message": line})
                summary["passed"] += 1
                summary["assertions"] += 1

        elif "failing:" in line.lower() or "[FAIL]" in line:
            if current_test:
                current_test["assertions"].append({"status": "fail", "message": line})
                summary["failed"] += 1
                summary["assertions"] += 1

        # Resumo final
        elif "passed" in line.lower() and "failed" in line.lower():
            import re
            nums = re.findall(r'(\d+)', line)
            if len(nums) >= 2:
                summary["passed"] = int(nums[0])
                summary["failed"] = int(nums[1])

    if current_test:
        tests.append(current_test)

    # Se não parseou nada, extrai números do fim
    if summary["assertions"] == 0:
        import re
        # Procura padrão: X passed, Y failed
        match = re.search(r'(\d+)\s*passed.*?(\d+)\s*failed', output, re.IGNORECASE)
        if match:
            summary["passed"] = int(match.group(1))
            summary["failed"] = int(match.group(2))
            summary["total"] = summary["passed"] + summary["failed"]

    summary["total"] = summary["passed"] + summary["failed"] + summary["pending"] + summary["errors"]

    return {
        "summary": summary,
        "tests": tests[-20:],  # últimos 20 testes
        "verdict": "PASS" if summary["failed"] == 0 and summary["errors"] == 0 else "FAIL",
    }
