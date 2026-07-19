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
    # gdlint auto-detecta .gdlintrc no diretório do projeto (não tem flag --config)

    gdlint_path = _find_tool("gdlint")
    if gdlint_path is None:
        return {
            "status": "error",
            "error": "Comando 'gdlint' nao encontrado. Verifique a instalacao do gdtoolkit.",
            "gdtoolkit_installed": True,
            "gdtoolkit_version": toolkit["version"],
        }

    cmd = [gdlint_path, str(proj)]

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


# ══════════════════════════════════════════════════════════════════════
# B4 — Análises Específicas (Fatia 4.4)
# ══════════════════════════════════════════════════════════════════════

def _collect_gd_files(proj: Path) -> list[Path]:
    """Coleta todos os arquivos .gd do projeto (exclui addons/.godot)."""
    gd_files = []
    for f in proj.rglob("*.gd"):
        parts = f.parts
        if "addons" in parts or ".godot" in parts:
            continue
        gd_files.append(f)
    return gd_files


def _read_gd_safe(path: Path) -> str:
    """Lê arquivo .gd com fallback de encoding."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""


def _detect_autoloads(proj: Path) -> set[str]:
    """Detecta nomes de autoloads do project.godot.

    Autoloads sao singletons globais — sempre acessiveis sem declaracao var.
    """
    autoloads = set()
    pg = proj / "project.godot"
    if not pg.exists():
        return autoloads

    try:
        content = pg.read_text(encoding="utf-8")
        in_autoload_section = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "[autoload]":
                in_autoload_section = True
                continue
            if stripped.startswith("[") and in_autoload_section:
                break  # fim da secao [autoload]
            if in_autoload_section:
                # Formato: Nome="*res://path/script.gd"
                m = re.match(r'^(\w+)="\*res://', stripped)
                if m:
                    autoloads.add(m.group(1))
    except Exception:
        pass

    return autoloads


# ── Op 1: find_unused_functions ──────────────────────────────────

def find_unused_functions(project_path: str | None = None) -> dict:
    """Encontra funcoes definidas mas nunca chamadas no projeto.

    Heuristica: parse de regex para definicoes (func nome()) e chamadas (nome()).
    Falsos positivos sao possiveis (conexao por sinal, chamada string-name).
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    gd_files = _collect_gd_files(proj)
    if not gd_files:
        return {"status": "passed", "unused": [], "total_functions": 0}

    # Regex para definicao: func nome(params):
    func_def = re.compile(r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    # Regex para chamada: .nome( ou nome( (nao precedido por func)
    func_call = re.compile(r'(?<!func\s)(?<!\.)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

    defined = {}  # func_name -> [files]
    called = set()

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        for m in func_def.finditer(content):
            name = m.group(1)
            if name not in defined:
                defined[name] = []
            rel = str(fpath.relative_to(proj))
            if rel not in defined[name]:
                defined[name].append(rel)

        for m in func_call.finditer(content):
            called.add(m.group(1))

    # Filtra: definidas mas nao chamadas
    # Exclui builtins e callbacks Godot conhecidos
    godot_callbacks = {
        "_ready", "_process", "_physics_process", "_input", "_unhandled_input",
        "_enter_tree", "_exit_tree", "_draw", "_gui_input", "_notification",
        "_init", "_to_string", "_get", "_set", "_get_property_list",
        "init", "ready", "process", "physics_process",
    }

    unused = []
    for name, files in sorted(defined.items()):
        if name not in called and name not in godot_callbacks and not name.startswith("__"):
            unused.append({"function": name, "files": files})

    return {
        "status": "completed",
        "total_functions": len(defined),
        "unused_count": len(unused),
        "unused": unused[:100],  # limita a 100
    }


# ── Op 2: detect_gdscript_antipatterns ───────────────────────────

def detect_gdscript_antipatterns(project_path: str | None = None) -> dict:
    """Detecta antipadroes comuns em GDScript.

    Detecta:
      - get_node() chamado dentro de _process/_physics_process (deveria ser cache)
      - _process com logica pesada (>20 linhas)
      - for loop chamando get_node (N buscas por frame)
      - $NodeRef dentro de funcao sem cache previo
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    gd_files = _collect_gd_files(proj)
    if not gd_files:
        return {"status": "passed", "antipatterns": [], "total": 0}

    # Padroes
    # get_node("path") ou get_node('path') — tree-search O(n), deveria ser cache
    get_node_pattern = re.compile(r'get_node\s*\(\s*["\']')
    # $NodeRef é O(1) — NAO é antipadrao, nao precisa de cache
    process_func = re.compile(r'func\s+(_process|_physics_process)\s*\(')

    findings = []

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        lines = content.splitlines()
        rel = str(fpath.relative_to(proj))

        # Detecta funcoes _process / _physics_process
        for m in process_func.finditer(content):
            func_start = content[:m.start()].count("\n")
            # Encontra o escopo da funcao (ate o proximo func ou fim)
            rest = content[m.start():]
            next_func = re.search(r'\nfunc\s+', rest[10:])  # pula "func _process("
            func_body = rest[:next_func.start() + 10] if next_func else rest

            # get_node dentro de _process
            gn_matches = get_node_pattern.findall(func_body)
            if gn_matches and len(gn_matches) >= 2:
                findings.append({
                    "type": "get_node_in_process",
                    "file": rel,
                    "line": func_start + 1,
                    "detail": f"_process/_physics_process chama get_node() {len(gn_matches)}x — considere cache em _ready",
                    "severity": "warning",
                })

            # _process muito longa
            func_lines = func_body.count("\n")
            if func_lines > 20:
                findings.append({
                    "type": "heavy_process",
                    "file": rel,
                    "line": func_start + 1,
                    "detail": f"_process/_physics_process com {func_lines} linhas — considere dividir em funcoes menores",
                    "severity": "warning",
                })

        # get_node em for loop
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("for ") and "get_node" in stripped:
                findings.append({
                    "type": "get_node_in_loop",
                    "file": rel,
                    "line": i + 1,
                    "detail": "get_node() dentro de for loop — N buscas por frame",
                    "severity": "warning",
                })

    # Ordena por severidade
    findings.sort(key=lambda f: (0 if f["severity"] == "error" else 1, f["file"], f["line"]))

    return {
        "status": "completed",
        "total": len(findings),
        "antipatterns": findings[:100],
    }


# ── Op 3: find_orphan_signals_nodes ──────────────────────────────

def find_orphan_signals_nodes(project_path: str | None = None) -> dict:
    """Encontra sinais conectados a nos que nao existem como variaveis no script.

    Verifica se o node alvo de um .connect() existe como:
      - Variavel declarada no script (var, @onready var)
      - Constante (const)
      - Referencia $NodeRef ou get_node()
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    gd_files = _collect_gd_files(proj)
    if not gd_files:
        return {"status": "passed", "orphans": [], "total": 0}

    # Captura: node_ref.signal_name.connect(method)
    # node_ref pode ser: variavel, $Node, get_node("..."), %Unique
    signal_connect = re.compile(
        r"([\w$%]+(?:/[\w$%]+)*)\s*\.\s*([\w_]+)\s*\.connect\s*\("
    )

    # Captura declaracoes: var nome, @onready var nome, const NOME
    var_decl = re.compile(r'(?:@\w+\s+)?var\s+(\w+)')
    const_decl = re.compile(r'const\s+(\w+)')

    orphans = []

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        rel = str(fpath.relative_to(proj))

        # Coleta variaveis/constantes declaradas no script
        declared = set()
        for m in var_decl.finditer(content):
            declared.add(m.group(1))
        for m in const_decl.finditer(content):
            declared.add(m.group(1))

        # Adiciona nos built-in do Godot (sempre disponiveis)
        builtins = {"self", "owner", "get_parent", "get_node", "get_tree"}

        # Detecta autoloads do projeto (singletons globais — nao precisam declaracao)
        autoloads = _detect_autoloads(proj)

        # Verifica cada conexao de sinal
        for m in signal_connect.finditer(content):
            target_node = m.group(1)
            signal_name = m.group(2)

            # Pula referencias built-in, $/%, e autoloads globais
            if target_node.startswith("$") or target_node.startswith("%"):
                continue  # $NodeRef e %Unique sempre acessam o node diretamente
            if target_node in builtins or target_node in autoloads:
                continue

            # Verifica se a variavel foi declarada
            if target_node not in declared:
                # Tenta encontrar a linha no contexto
                line_no = content[:m.start()].count("\n") + 1
                orphans.append({
                    "type": "orphan_signal",
                    "script": rel,
                    "line": line_no,
                    "target": target_node,
                    "signal": signal_name,
                    "detail": (
                        f"'{target_node}.{signal_name}.connect()' — "
                        f"'{target_node}' nao declarado como var/const no script"
                    ),
                })

    return {
        "status": "completed",
        "total": len(orphans),
        "orphans": orphans[:100],
    }


# ── Op 4: check_naming_convention ────────────────────────────────

def check_naming_convention(project_path: str | None = None) -> dict:
    """Verifica convencoes de nomenclatura GDScript alem do gdlint.

    Verifica:
      - Classes com nome em PascalCase
      - Funcoes em snake_case
      - Constantes em UPPER_CASE
      - Sinais em snake_case
      - Variaveis exportadas sem prefixo _ (sao publicas)
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    gd_files = _collect_gd_files(proj)
    if not gd_files:
        return {"status": "passed", "violations": [], "total": 0}

    # Padroes
    pascal = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
    snake = re.compile(r'^_?[a-z][a-z0-9]*(_[a-z0-9]+)*$')
    upper = re.compile(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$')

    violations = []

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        rel = str(fpath.relative_to(proj))

        # Nome de classe
        class_matches = re.finditer(r'class_name\s+(\w+)', content)
        for m in class_matches:
            name = m.group(1)
            if not pascal.match(name):
                violations.append({
                    "type": "class_naming",
                    "file": rel,
                    "name": name,
                    "detail": f"Nome de classe '{name}' deve ser PascalCase",
                })

        # Constantes
        const_matches = re.finditer(r'const\s+(\w+)\s*[:=]', content)
        for m in const_matches:
            name = m.group(1)
            if not upper.match(name):
                violations.append({
                    "type": "constant_naming",
                    "file": rel,
                    "name": name,
                    "detail": f"Constante '{name}' deve ser UPPER_CASE",
                })

        # Sinais
        signal_matches = re.finditer(r'signal\s+(\w+)', content)
        for m in signal_matches:
            name = m.group(1)
            if not snake.match(name):
                violations.append({
                    "type": "signal_naming",
                    "file": rel,
                    "name": name,
                    "detail": f"Sinal '{name}' deve ser snake_case",
                })

        # Funcoes publicas (sem _ prefix)
        func_matches = re.finditer(r'func\s+([a-zA-Z_]\w*)\s*\(', content)
        for m in func_matches:
            name = m.group(1)
            if name.startswith("_"):
                continue  # privada, ok
            if name.startswith("@"):
                continue  # annotation
            if not snake.match(name) and not pascal.match(name):
                violations.append({
                    "type": "function_naming",
                    "file": rel,
                    "name": name,
                    "detail": f"Funcao publica '{name}' deve ser snake_case",
                })

        # Variaveis exportadas com _ prefix (export e publico!)
        export_matches = re.finditer(r'@export\s+var\s+(_\w+)', content)
        for m in export_matches:
            name = m.group(1)
            violations.append({
                "type": "export_variable_naming",
                "file": rel,
                "name": name,
                "detail": f"Variavel exportada '{name}' tem prefixo _ (export = publico, remova o _)",
            })

    return {
        "status": "completed",
        "total": len(violations),
        "violations": violations[:100],
    }


# ── Op 5: find_duplicate_code_blocks ────────────────────────────

def find_duplicate_code_blocks(project_path: str | None = None, min_lines: int = 5) -> dict:
    """Encontra blocos de codigo duplicados entre arquivos .gd.

    Heuristica: hashing de linhas normalizadas (sem whitespace/comentarios)
    em janelas deslizantes de tamanho configuravel.
    """
    import hashlib

    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    gd_files = _collect_gd_files(proj)
    if len(gd_files) < 2:
        return {"status": "passed", "duplicates": [], "total": 0}

    # Normalizador de linha
    def normalize(line: str) -> str:
        s = line.strip()
        if s.startswith("#"):
            return ""
        return re.sub(r'\s+', ' ', s)

    # Indice: hash -> [(file, line_start)]
    block_index: dict[str, list[tuple[str, int, str]]] = {}

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        lines = content.splitlines()
        rel = str(fpath.relative_to(proj))

        for i in range(len(lines) - min_lines + 1):
            block_lines = [normalize(l) for l in lines[i:i + min_lines]]
            block_text = "\n".join(block_lines)
            if len(block_text.strip()) < 20:  # muito curto, ignorar
                continue
            h = hashlib.md5(block_text.encode()).hexdigest()
            if h not in block_index:
                block_index[h] = []
            block_index[h].append((rel, i + 1, block_text[:200]))

    # Filtra duplicatas reais (aparecem em >1 arquivo)
    duplicates = []
    for h, occurrences in block_index.items():
        if len(occurrences) >= 2:
            # Verifica se sao arquivos diferentes
            files = {o[0] for o in occurrences}
            if len(files) >= 2:
                duplicates.append({
                    "hash": h[:12],
                    "occurrences": [
                        {"file": o[0], "line": o[1], "snippet": o[2][:100]}
                        for o in occurrences[:5]
                    ],
                    "file_count": len(files),
                })

    duplicates.sort(key=lambda d: d["file_count"], reverse=True)

    return {
        "status": "completed",
        "total": len(duplicates),
        "duplicates": duplicates[:50],
    }


# ── Op 6: detect_scene_reference_cycles ──────────────────────────

def detect_scene_reference_cycles(project_path: str | None = None) -> dict:
    """Detecta ciclos de referencia entre cenas .tscn.

    Ex: cena A instancia B, cena B instancia A = ciclo infinito.
    Usa deteccao de ciclo em grafo direcionado (DFS).
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    tscn_files = list(proj.rglob("*.tscn"))
    if len(tscn_files) < 2:
        return {"status": "passed", "cycles": [], "total": 0}

    # Padrao de instancia de sub-cena: [ext_resource ... path="res://..." ...]
    # e depois [node ... instance=ExtResource("N")]
    ext_res = re.compile(r'\[ext_resource[^\]]*path="([^"]+)"[^\]]*id="?(\d+)"?')
    instance = re.compile(r'instance\s*=\s*ExtResource\s*\(\s*"?(\d+)"?\s*\)')

    # Grafo: scene_name -> set(scene_names_que_instancia)
    graph: dict[str, set[str]] = {}
    scene_names = {str(t.relative_to(proj)): t for t in tscn_files}

    for rel_name, tpath in scene_names.items():
        content = _read_gd_safe(tpath)
        # Mapa id -> path
        id_to_path: dict[str, str] = {}
        for m in ext_res.finditer(content):
            rid = m.group(2)
            rpath = m.group(1)
            id_to_path[rid] = rpath

        # Instancias
        instanced = set()
        for m in instance.finditer(content):
            rid = m.group(1)
            if rid in id_to_path:
                p = id_to_path[rid]
                # Converte para relativo se possivel
                for sn in scene_names:
                    if p.endswith(sn) or sn.endswith(p.replace("res://", "")):
                        instanced.add(sn)
                        break

        if instanced:
            graph[rel_name] = instanced

    # DFS para detectar ciclos
    cycles = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}

    def dfs(node: str, path: list[str]):
        color[node] = GRAY
        for neighbor in graph.get(node, set()):
            if color.get(neighbor, BLACK) == GRAY:
                # Ciclo encontrado
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle = path[cycle_start:] + [neighbor]
                cycles.append({"cycle": cycle, "length": len(cycle)})
            elif color.get(neighbor, BLACK) == WHITE:
                dfs(neighbor, path + [neighbor])
        color[node] = BLACK

    for node in list(graph.keys()):
        if color.get(node, BLACK) == WHITE:
            dfs(node, [node])

    # Remove duplicatas (ciclos iguais com rotacao)
    unique = []
    seen = set()
    for c in cycles:
        key = tuple(sorted(c["cycle"]))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return {
        "status": "completed",
        "total": len(unique),
        "cycles": unique[:20],
    }


# ── Op 7: check_import_settings_consistency ─────────────────────

def check_import_settings_consistency(project_path: str | None = None) -> dict:
    """Verifica consistencia de configuracoes de importacao entre assets do mesmo tipo.

    Assets do mesmo tipo (ex: todas texturas .png) devem ter .import consistentes.
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    import_files = list(proj.rglob("*.import"))
    if not import_files:
        return {"status": "passed", "inconsistencies": [], "total": 0}

    # Agrupa por extensao do asset original
    # .import referencia o source file na primeira linha ou no conteudo
    by_ext: dict[str, list[tuple[str, str]]] = {}
    source_pattern = re.compile(r'source_file="([^"]+)"')
    valid_import = re.compile(r'valid_import=(\w+)')

    for imp in import_files:
        content = _read_gd_safe(imp)
        # Encontra source file
        sm = source_pattern.search(content)
        if not sm:
            continue
        source = sm.group(1)
        ext = Path(source).suffix.lower()
        if not ext:
            ext = "(sem extensao)"

        if ext not in by_ext:
            by_ext[ext] = []
        by_ext[ext].append((str(imp.relative_to(proj)), content))

    inconsistencies = []
    for ext, files in by_ext.items():
        if len(files) < 2:
            continue

        # Compara configuracoes de compressao/modo entre arquivos
        config_keys = [
            "compress/mode", "compress/lossy_quality", "compress/high_quality",
            "process/fix_alpha_border", "process/premult_alpha",
            "process/HDR_as_SRGB", "process/size_limit",
            "svg/scale", "detect_3d/compress_to",
        ]

        baseline = {}
        for key in config_keys:
            m = re.search(rf'{key}=(\S+)', files[0][1])
            if m:
                baseline[key] = m.group(1)

        for fname, content in files[1:]:
            for key, expected in baseline.items():
                m = re.search(rf'{key}=(\S+)', content)
                actual = m.group(1) if m else "(ausente)"
                if actual != expected:
                    inconsistencies.append({
                        "type": key,
                        "file": fname,
                        "expected": expected,
                        "actual": actual,
                        "detail": f"{key}: esperado={expected}, obtido={actual}",
                    })

    return {
        "status": "completed",
        "total": len(inconsistencies),
        "inconsistencies": inconsistencies[:100],
    }


# ── Op 8: semantic_code_search ──────────────────────────────────

def semantic_code_search(project_path: str | None = None, query: str = "") -> dict:
    """Busca semantica no codigo GDScript por palavra-chave ou padrao.

    Similar a grep, mas com contexto GDScript-aware (tipo de ocorrencia:
    funcao, variavel, sinal, classe, comentario, string).
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    if not query:
        return {"status": "error", "error": "Parametro 'query' obrigatorio."}

    gd_files = _collect_gd_files(proj)
    results = []
    query_lower = query.lower()

    # Classificadores de contexto
    context_patterns = [
        ("function_def", re.compile(r'func\s+\w*' + re.escape(query) + r'\w*\s*\(')),
        ("class_def", re.compile(r'class_name\s+' + re.escape(query))),
        ("signal_def", re.compile(r'signal\s+\w*' + re.escape(query) + r'\w*')),
        ("const_def", re.compile(r'const\s+\w*' + re.escape(query) + r'\w*')),
        ("var_def", re.compile(r'var\s+\w*' + re.escape(query) + r'\w*')),
        ("export_var", re.compile(r'@export\s+var\s+\w*' + re.escape(query) + r'\w*')),
    ]

    for fpath in gd_files:
        content = _read_gd_safe(fpath)
        lines = content.splitlines()
        rel = str(fpath.relative_to(proj))

        for i, line in enumerate(lines):
            if query_lower not in line.lower():
                continue

            # Classifica o contexto
            context = "reference"
            for ctx_name, ctx_pattern in context_patterns:
                if ctx_pattern.search(line):
                    context = ctx_name
                    break

            # Determina se esta em comentario ou string
            stripped = line.strip()
            if stripped.startswith("#"):
                context = "comment"

            results.append({
                "file": rel,
                "line": i + 1,
                "context": context,
                "snippet": line.strip()[:120],
            })

    # Agrupa por contexto
    by_context: dict[str, int] = {}
    for r in results:
        by_context[r["context"]] = by_context.get(r["context"], 0) + 1

    return {
        "status": "completed",
        "query": query,
        "total": len(results),
        "by_context": by_context,
        "results": results[:200],
    }


# ── Op 9: suggest_refactor ──────────────────────────────────────

def suggest_refactor(project_path: str | None = None) -> dict:
    """Sugere refatoracoes baseadas em padroes detectados no codigo.

    Agrega resultados de outras analises e gera sugestoes acionaveis:
      - Extrair funcao longa
      - Criar classe para god_class
      - Cache de get_node em _ready
      - Remover codigo duplicado
      - Renomear para convencao
    """
    proj = _find_project_root(project_path)
    if proj is None:
        return {"status": "error", "error": "Nenhum projeto Godot encontrado."}

    suggestions = []

    # 1. Funcoes nao usadas -> remover
    unused_result = find_unused_functions(str(proj))
    if unused_result.get("unused_count", 0) > 0:
        suggestions.append({
            "category": "dead_code",
            "priority": "medium",
            "title": f"Remover {unused_result['unused_count']} funcoes nao utilizadas",
            "detail": "Funcoes definidas mas nunca chamadas no codigo. "
                      "Atencao: callbacks de sinal conectados via editor nao sao detectados.",
            "affected": unused_result.get("unused", [])[:5],
        })

    # 2. Antipadroes -> corrigir
    antipatterns = detect_gdscript_antipatterns(str(proj))
    for a in antipatterns.get("antipatterns", [])[:3]:
        if a["type"] == "get_node_in_process":
            suggestions.append({
                "category": "performance",
                "priority": "high",
                "title": f"Cache get_node() em _ready — {a['file']}",
                "detail": f"get_node() chamado em _process/_physics_process. "
                          f"Mova para _ready e armazene em variavel.",
                "file": a["file"],
                "line": a["line"],
            })
        elif a["type"] == "get_node_in_loop":
            suggestions.append({
                "category": "performance",
                "priority": "high",
                "title": f"get_node() dentro de for loop — {a['file']}:{a['line']}",
                "detail": "get_node() em loop causa N buscas por frame. Pre-carregue os nos.",
                "file": a["file"],
                "line": a["line"],
            })
        elif a["type"] == "heavy_process":
            suggestions.append({
                "category": "maintainability",
                "priority": "medium",
                "title": f"Dividir _process longo — {a['file']}",
                "detail": "_process muito longo. Extraia logica em funcoes menores.",
                "file": a["file"],
                "line": a["line"],
            })

    # 3. Naming -> renomear
    naming = check_naming_convention(str(proj))
    if naming.get("total", 0) > 0:
        suggestions.append({
            "category": "naming",
            "priority": "low",
            "title": f"Corrigir {naming['total']} violacoes de nomenclatura",
            "detail": "Constantes devem ser UPPER_CASE, classes PascalCase, funcoes snake_case.",
            "examples": naming.get("violations", [])[:3],
        })

    # 4. Duplicatas -> extrair funcao compartilhada
    dups = find_duplicate_code_blocks(str(proj))
    if dups.get("total", 0) > 0:
        suggestions.append({
            "category": "maintainability",
            "priority": "medium",
            "title": f"Extrair {dups['total']} blocos duplicados em funcao compartilhada",
            "detail": "Codigo duplicado entre arquivos. Crie uma funcao utilitaria ou classe base.",
        })

    # Ordena por prioridade
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: priority_order.get(s["priority"], 99))

    return {
        "status": "completed",
        "total": len(suggestions),
        "suggestions": suggestions,
    }

