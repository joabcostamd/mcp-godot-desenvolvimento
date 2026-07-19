"""code_quality_ops.py — gdtoolkit Integration (Fatia 4.3 / Etapa B3).

Integra gdtoolkit (gdlint + gdformat + gdradon) como gate de qualidade
dentro do run_verification_pipeline.

Ferramentas:
- run_gdlint       — análise estática de GDScript (god_class, função longa, etc.)
- run_gdformat_check — verifica formatação sem modificar arquivos
- run_gdradon      — análise de complexidade ciclomática
- run_code_quality_gate — orquestrador: roda todos e retorna gate PASS/FAIL
"""

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _find_project_root(project_path: str | None = None) -> Path | None:
    """Resolve o diretório do projeto Godot."""
    if project_path:
        p = Path(project_path)
        if (p / "project.godot").exists():
            return p
        return None

    # Tenta projeto ativo
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        pass

    # Fallback: usa raiz do MCP se houver project.godot
    if (ROOT / "project.godot").exists():
        return ROOT

    return None


def _find_tool(name: str) -> str | None:
    """Encontra o caminho completo de um executavel do gdtoolkit.

    Tenta shutil.which() (PATH) e fallback para <venv>/Scripts/<name>.exe.
    """
    # 1. shutil.which — funciona se venv estiver no PATH
    found = shutil.which(name)
    if found:
        return found

    # 2. Fallback: busca no Scripts do venv atual
    venv_scripts = Path(sys.executable).parent
    candidate = venv_scripts / f"{name}.exe"
    if candidate.exists():
        return str(candidate)

    # 3. Fallback: busca no Scripts relativo ao ROOT
    candidate2 = ROOT / ".venv" / "Scripts" / f"{name}.exe"
    if candidate2.exists():
        return str(candidate2)

    return None


def _ensure_gdtoolkit() -> dict:
    """Verifica se gdtoolkit está instalado (gdlint + gdformat + gdradon).

    Tenta gdlint --version como proxy. Se falhar, assume que todo o toolkit
    está ausente (instalacao tipica via pip install gdtoolkit).
    """
    gdlint_path = _find_tool("gdlint")
    if gdlint_path is None:
        return {
            "installed": False,
            "error": (
                "gdtoolkit nao encontrado. Instale com: "
                "pip install 'gdtoolkit>=4.0,<5.0'"
            ),
        }

    try:
        result = subprocess.run(
            [gdlint_path, "--version"],
            capture_output=True, text=True, timeout=10,
            stdin=subprocess.DEVNULL,
        )
        version = result.stdout.strip() or result.stderr.strip()
        if not version:
            version = "(versao desconhecida)"
        return {"installed": True, "version": version}
    except subprocess.TimeoutExpired:
        return {"installed": False, "error": "Timeout ao verificar gdtoolkit."}
    except Exception as e:
        return {"installed": False, "error": f"Erro ao verificar gdtoolkit: {e}"}


def _locate_gdlintrc(project_path: Path) -> Path | None:
    """Localiza .gdlintrc: raiz do projeto > raiz do MCP."""
    candidates = [
        project_path / ".gdlintrc",
        ROOT / ".gdlintrc",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _parse_gdlint_output(output: str) -> dict:
    """Faz parse do output do gdlint para dict estruturado.

    Usa regex robusto para compatibilidade com paths Windows
    (ex: C:\\project\\file.gd), paths relativos e absolutos.

    Formato típico:
      file.gd:10: Error: function-too-long (msg)
      C:\\project\\file.gd:42: Warning: unused-argument (msg)
    """
    violations = []
    summary = {"error": 0, "warning": 0, "style": 0, "total": 0}

    # Regex: path:linha: Severidade: código(mensagem)
    # Grupo 1: path (pode conter : em drive letter Windows)
    # Grupo 2: número da linha
    # Grupo 3: severidade (Error/Warning/Style/Fatal/Info/Warn)
    # Grupo 4: código + mensagem
    # Usa .+ (greedy) + backtrack — mais eficiente que .+? para este formato
    pattern = re.compile(
        r'^(.+):(\d+):\s*'
        r'(Error|Warning|Style|Fatal|Info|Warn)'
        r':\s*(.+)$'
    )

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Pre-filtro rápido: linha precisa conter padrão :NN: Severidade:
        if not re.search(r':\d+:\s*(Error|Warning|Style|Fatal|Info|Warn):', line):
            continue

        m = pattern.match(line)
        if not m:
            continue

        file_path = m.group(1).strip()
        try:
            line_no = int(m.group(2))
        except ValueError:
            continue

        severity = m.group(3).strip().lower()
        code_and_msg = m.group(4).strip()

        # Separa código da mensagem: "code (mensagem)" ou "code"
        code_parts = code_and_msg.split("(", 1)
        code = code_parts[0].strip()
        if len(code_parts) > 1:
            message = code_parts[1].rstrip(")").strip()
        else:
            message = code_and_msg

        # Classifica severidade
        if severity in ("error", "fatal"):
            summary["error"] += 1
        elif severity in ("warning", "warn"):
            summary["warning"] += 1
        else:
            summary["style"] += 1
        summary["total"] += 1

        violations.append({
            "file": file_path,
            "line": line_no,
            "severity": severity,
            "code": code,
            "message": message,
        })

    # Ordena por severidade (error > warning > style)
    severity_order = {"error": 0, "fatal": 0, "warning": 1, "warn": 1, "style": 2}
    violations.sort(key=lambda v: (severity_order.get(v["severity"], 99), v["file"], v["line"]))

    return {
        "violations": violations,
        "summary": summary,
    }


# ══════════════════════════════════════════════════════════════════════
# Operações Individuais
# ══════════════════════════════════════════════════════════════════════

def run_gdlint(project_path: str | None = None) -> dict:
    """Executa gdlint (análise estática) no projeto Godot.

    Detecta: god_class, função longa, complexidade ciclomática,
    nomeação inconsistente, parâmetros em excesso, aninhamento profundo,
    variável não usada, e outros problemas de estilo.

    Args:
        project_path: Caminho do projeto. Se omitido, usa projeto ativo.

    Returns:
        dict com violations e summary.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {
            "status": "error",
            "error": "Nenhum projeto Godot encontrado. Defina um projeto ativo ou passe project_path.",
        }

    toolkit = _ensure_gdtoolkit()
    if not toolkit["installed"]:
        return {
            "status": "error",
            "error": toolkit["error"],
            "gdtoolkit_installed": False,
        }

    start = time.time()
    config = _locate_gdlintrc(proj)

    gdlint_path = _find_tool("gdlint")
    if gdlint_path is None:
        return {
            "status": "error",
            "error": "Comando 'gdlint' nao encontrado. Verifique a instalacao do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    cmd = [gdlint_path]
    if config:
        cmd.extend(["--config", str(config)])
    cmd.append(str(proj))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120,
            cwd=str(proj),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Timeout (120s) ao executar gdlint. Projeto muito grande?",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "Comando 'gdlint' não encontrado. Verifique a instalação do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Erro ao executar gdlint: {e}",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    elapsed_ms = round((time.time() - start) * 1000)
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    parsed = _parse_gdlint_output(output)
    has_errors = parsed["summary"]["error"] > 0

    return {
        "status": "failed" if has_errors else "passed",
        "gdtoolkit_version": toolkit["version"],
        "config_used": str(config) if config else "default",
        "duration_ms": elapsed_ms,
        "exit_code": result.returncode,
        **parsed,
    }


def run_gdformat_check(project_path: str | None = None) -> dict:
    """Verifica formatação GDScript (gdformat --check) sem modificar arquivos.

    Args:
        project_path: Caminho do projeto. Se omitido, usa projeto ativo.

    Returns:
        dict com lista de arquivos mal formatados e diff.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {
            "status": "error",
            "error": "Nenhum projeto Godot encontrado.",
        }

    toolkit = _ensure_gdtoolkit()
    if not toolkit["installed"]:
        return {
            "status": "error",
            "error": toolkit["error"],
            "gdtoolkit_installed": False,
        }

    start = time.time()

    gdformat_path = _find_tool("gdformat")
    if gdformat_path is None:
        return {
            "status": "error",
            "error": "Comando 'gdformat' nao encontrado. Verifique a instalacao do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    try:
        result = subprocess.run(
            [gdformat_path, "--check", "--diff", str(proj)],
            capture_output=True, text=True, timeout=120,
            cwd=str(proj),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Timeout (120s) ao executar gdformat.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "Comando 'gdformat' não encontrado. Verifique a instalação do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Erro ao executar gdformat: {e}",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    elapsed_ms = round((time.time() - start) * 1000)
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    # gdformat --check retorna !=0 se arquivos precisam de formatação
    needs_formatting = result.returncode != 0

    # Extrai lista de arquivos mal formatados via regex (robusto)
    unformatted_files = []
    # Padrão: "would reformat <path>" ou "would format <path>"
    fmt_pattern = re.compile(r'would (reformat|format)\s+(.+\.gd)', re.IGNORECASE)
    for line in output.splitlines():
        m = fmt_pattern.search(line)
        if m:
            unformatted_files.append(m.group(2).strip())

    return {
        "status": "failed" if needs_formatting else "passed",
        "needs_formatting": needs_formatting,
        "unformatted_count": len(unformatted_files),
        "unformatted_files": unformatted_files[:50],  # limita a 50
        "gdtoolkit_version": toolkit["version"],
        "duration_ms": elapsed_ms,
        "exit_code": result.returncode,
        "raw_output_tail": output[-2000:] if len(output) > 2000 else output,
    }


def run_gdradon(project_path: str | None = None) -> dict:
    """Analisa complexidade do código GDScript via gdradon.

    Mede: complexidade ciclomática, linhas por função, god_class score,
    maintainability index aproximado.

    Args:
        project_path: Caminho do projeto. Se omitido, usa projeto ativo.

    Returns:
        dict com métricas de complexidade por arquivo e sumário.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {
            "status": "error",
            "error": "Nenhum projeto Godot encontrado.",
        }

    toolkit = _ensure_gdtoolkit()
    if not toolkit["installed"]:
        return {
            "status": "error",
            "error": toolkit["error"],
            "gdtoolkit_installed": False,
        }

    start = time.time()

    gdradon_path = _find_tool("gdradon")
    if gdradon_path is None:
        return {
            "status": "error",
            "error": "Comando 'gdradon' nao encontrado. Verifique a instalacao do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    # gdradon cc <path> (sem flags extras — gdtoolkit 4.x não aceita --show-complexity)
    try:
        result = subprocess.run(
            [gdradon_path, "cc", str(proj)],
            capture_output=True, text=True, timeout=120,
            cwd=str(proj),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Timeout (120s) ao executar gdradon.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "Comando 'gdradon' não encontrado. Verifique a instalação do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Erro ao executar gdradon: {e}",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    elapsed_ms = round((time.time() - start) * 1000)
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    # Se exit code != 0, pode ser erro ou apenas avisos
    # Parse do output do gdradon
    # Formato típico:
    #   path/file.gd
    #       F 5:0 func_name - A (5)
    #   X blocks (classes), Y functions, Z lines, complexity A
    complexity_data = _parse_gdradon_output(output)

    return {
        "status": "completed",
        "gdtoolkit_version": toolkit["version"],
        "duration_ms": elapsed_ms,
        "exit_code": result.returncode,
        **complexity_data,
    }


def _parse_gdradon_output(output: str) -> dict:
    """Parse do output do gdradon cc para dict estruturado."""
    files = []
    current_file = None
    total_functions = 0
    total_complexity = 0
    max_complexity = 0
    max_complexity_func = ""

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # Linha de arquivo (não indentada, termina com .gd)
        if not line.startswith(" ") and not line.startswith("\t") and stripped.endswith(".gd"):
            if current_file:
                files.append(current_file)
            current_file = {
                "file": stripped,
                "functions": [],
                "file_complexity": 0,
            }
            continue

        # Linha de função (indentada): F linha:coluna nome - nota (complexidade)
        if current_file and stripped.startswith("F "):
            parts = stripped[2:].strip().split(" - ", 1)
            if len(parts) >= 2:
                location_name = parts[0].strip()
                grade_complexity = parts[1].strip()

                # Extrai localização, nome
                loc_parts = location_name.split(" ", 1)
                location = loc_parts[0] if loc_parts else ""
                func_name = loc_parts[1] if len(loc_parts) > 1 else location_name

                # Extrai nota e complexidade: "A (3)" ou "C (12)"
                grade = "?"
                complexity = 0
                grade_parts = grade_complexity.split("(", 1)
                if len(grade_parts) >= 2:
                    grade = grade_parts[0].strip()
                    try:
                        complexity = int(grade_parts[1].rstrip(")"))
                    except ValueError:
                        pass

                current_file["functions"].append({
                    "name": func_name,
                    "location": location,
                    "grade": grade,
                    "complexity": complexity,
                })
                current_file["file_complexity"] += complexity
                total_functions += 1
                total_complexity += complexity

                if complexity > max_complexity:
                    max_complexity = complexity
                    max_complexity_func = f"{func_name} ({current_file['file']}:{location})"

        # Linha de sumário do arquivo
        elif current_file and ("blocks" in stripped.lower() or "functions" in stripped.lower()):
            pass  # Sumário por arquivo — ignoramos

    # Não esquecer o último arquivo
    if current_file:
        files.append(current_file)

    avg_complexity = round(total_complexity / max(total_functions, 1), 1)

    # Identifica arquivos problemáticos (complexidade total alta)
    high_complexity_files = [
        f for f in files
        if f["file_complexity"] > 50  # threshold arbitrário
    ]
    high_complexity_files.sort(key=lambda f: f["file_complexity"], reverse=True)

    return {
        "files_analyzed": len(files),
        "total_functions": total_functions,
        "total_complexity": total_complexity,
        "average_complexity": avg_complexity,
        "max_complexity": max_complexity,
        "max_complexity_function": max_complexity_func,
        "high_complexity_files": [
            {"file": f["file"], "total_complexity": f["file_complexity"]}
            for f in high_complexity_files[:10]
        ],
        "all_files": files,  # completo — pode ser grande
    }


# ══════════════════════════════════════════════════════════════════════
# Gate Orquestrador (usado pelo run_verification_pipeline)
# ══════════════════════════════════════════════════════════════════════

def run_code_quality_gate(project_path: str | None = None) -> dict:
    """Executa o gate completo de qualidade de código.

    Roda gdlint → gdformat --check → gdradon em sequência.
    O gate FALHA se:
      - gdlint encontra erros (severity=error/fatal)
      - gdformat encontra arquivos mal formatados
    O gdradon é INFORMATIVO (não bloqueia o gate, mas reporta métricas).

    Args:
        project_path: Caminho do projeto.

    Returns:
        dict com status do gate + resultados de cada ferramenta.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {
            "status": "error",
            "gate_passed": False,
            "error": "Nenhum projeto Godot encontrado.",
        }

    toolkit = _ensure_gdtoolkit()
    if not toolkit["installed"]:
        return {
            "status": "skipped",
            "gate_passed": True,  # Não bloqueia se a ferramenta não está instalada
            "reason": toolkit["error"],
            "gdtoolkit_installed": False,
        }

    gate_start = time.time()
    results = {}

    # 1. gdlint (BLOQUEANTE se erros)
    lint_result = run_gdlint(str(proj))
    results["gdlint"] = lint_result

    # 2. gdformat --check (BLOQUEANTE se mal formatado)
    fmt_result = run_gdformat_check(str(proj))
    results["gdformat"] = fmt_result

    # 3. gdradon (INFORMATIVO)
    radon_result = run_gdradon(str(proj))
    results["gdradon"] = radon_result

    elapsed_total = round((time.time() - gate_start) * 1000)

    # Determina se o gate passou
    # gdlint: falha se status="failed" (violações) ou status="error" (erro de execução)
    lint_status = lint_result.get("status")
    lint_failed = lint_status in ("failed", "error")

    # gdformat: falha se needs_formatting=True
    fmt_failed = fmt_result.get("needs_formatting", False)

    gate_passed = not lint_failed and not fmt_failed

    # Sumário textual
    summary_parts = []
    if lint_status == "error":
        summary_parts.append(f"gdlint: ERROR ({lint_result.get('error', 'erro desconhecido')[:80]})")
    else:
        lint_count = lint_result.get("summary", {}).get("total", 0)
        summary_parts.append(f"gdlint: {'PASS' if not lint_failed else f'FAIL ({lint_count} violações)'}")
    unformatted = fmt_result.get("unformatted_count", 0)
    summary_parts.append(f"gdformat: {'PASS' if not fmt_failed else f'FAIL ({unformatted} arquivos)'}")
    avg_cc = radon_result.get("average_complexity", "?")
    summary_parts.append(f"gdradon: avg CC={avg_cc}")

    return {
        "status": "failed" if not gate_passed else "passed",
        "gate_passed": gate_passed,
        "gdtoolkit_version": toolkit["version"],
        "summary": " | ".join(summary_parts),
        "lint_failed": lint_failed,
        "fmt_failed": fmt_failed,
        "total_duration_ms": elapsed_total,
        "project_path": str(proj),
        "results": results,
    }
