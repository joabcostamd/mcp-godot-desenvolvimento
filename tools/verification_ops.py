"""verification_ops.py — Pipeline de Verificação (item 1 do plano de evolução).

Executa até 6 etapas sequenciais em um projeto Godot:
  1. Compile Check  — força parse de todos os scripts (godot --headless --quit)
  2. Headless Run   — executa cena de teste e captura stdout/stderr
  3. Screenshot     — captura frame após N frames via --write-movie
  4. GUT Tests      — roda suíte de testes unitários (opcional)
  5. Reachability   — auditoria de cenas órfãs (opcional)
  6. Code Quality   — gate gdtoolkit (gdlint + gdformat + gdradon) (Fatia 4.3)

Tool: run_verification_pipeline — executa as etapas e retorna relatório consolidado.
"""

import base64
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Code Quality Gate (Fatia 4.3 / Etapa B3) ────────────────────────
try:
    from tools.code_quality_ops import run_code_quality_gate
except ImportError:
    run_code_quality_gate = None  # graceful degradation


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _resolve_project(project_path: str | None) -> Path | None:
    """Resolve o caminho do projeto: explícito ou via active project."""
    if project_path:
        return Path(project_path)
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        return None


def _resolve_godot(godot_path: str | None) -> str:
    """Resolve o executável do Godot."""
    if godot_path:
        return godot_path
    try:
        from tools.classdb import get_godot_bin
        return get_godot_bin()
    except Exception:
        return "godot"


def _read_project_godot(proj: Path) -> dict:
    """Lê project.godot e retorna dict com settings relevantes."""
    pg = proj / "project.godot"
    if not pg.exists():
        return {}
    try:
        import godot_parser as gp
        data = gp.load(str(pg))
        return data if isinstance(data, dict) else {}
    except Exception:
        # Fallback: parse INI-like manual
        settings = {}
        current_section = None
        try:
            for line in pg.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                elif "=" in line and current_section:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"')
                    settings[f"{current_section}/{key}"] = val
        except Exception:
            pass
        return settings


def _extract_errors(output: str) -> list[str]:
    """Extrai linhas de erro de stdout/stderr."""
    errors = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(kw in stripped for kw in (
            "ERROR:", "SCRIPT ERROR", "Parse Error",
            "error:", "SCRIPT ERROR:", "Failed to load",
        )):
            errors.append(stripped)
    return errors


def _detect_crash(output: str, exit_code: int) -> dict:
    """Analisa stdout/stderr para detectar crash."""
    crashed = False
    stacktrace = []
    
    # Crash por exit code não-zero (não confundir com quit() normal)
    if exit_code != 0:
        # Verifica se é crash real ou quit(1) intencional
        crash_kws = ["Crash", "FATAL", "Aborted", "SEGV", "Access violation",
                     "Condition", "p_error", "index", "Signal", "Exception"]
        has_crash_signal = any(kw in output for kw in crash_kws)
        has_error = bool(_extract_errors(output))
        if has_crash_signal or has_error:
            crashed = True
    
    # Stacktrace: procura linhas com padrão de trace
    trace_lines = []
    in_trace = False
    for line in output.splitlines():
        stripped = line.strip()
        if re.match(r'^\s*(at:|\[0x|\w+\.gd:\d+)', stripped):
            in_trace = True
        if in_trace:
            trace_lines.append(stripped)
            if not stripped:
                in_trace = False
    
    if trace_lines:
        crashed = True
        stacktrace = trace_lines
    
    return {"crashed": crashed, "stacktrace": stacktrace if stacktrace else None}


def _resolve_test_scene(proj: Path, test_scene: str | None = None) -> str | None:
    """Determina a cena de teste: parâmetro > project.godot > None."""
    if test_scene:
        return test_scene

    settings = _read_project_godot(proj)
    # godot_parser retorna dict aninhado: {"application": {"run/main_scene": "..."}}
    # Fallback retorna chaves planas: {"application/run/main_scene": "..."}
    run_main = (
        settings.get("application", {}).get("run/main_scene")
        if isinstance(settings.get("application"), dict)
        else settings.get("application/run/main_scene")
    )
    if run_main:
        # Garante prefixo res://
        scene = run_main.strip()
        if not scene.startswith("res://"):
            scene = "res://" + scene.lstrip("/")
        return scene

    return None


# ══════════════════════════════════════════════════════════════════════
# Etapas do Pipeline
# ══════════════════════════════════════════════════════════════════════

def _step_compile(proj: Path, godot: str, timeout: int) -> dict:
    """Etapa 1: Força parse de todos os scripts do projeto."""
    start = time.time()

    if not (proj / "project.godot").exists():
        return {
            "status": "failed",
            "error": f"project.godot nao encontrado em {proj}",
            "duration_ms": 0,
        }

    try:
        result = subprocess.run(
            [godot, "--headless", "--quit", "--path", str(proj)],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "error": f"Timeout ({timeout}s) no compile check. Verifique se o projeto carrega sem erros.",
            "duration_ms": int(timeout * 1000),
        }
    except FileNotFoundError:
        return {
            "status": "failed",
            "error": f"Godot executavel nao encontrado: {godot}",
            "duration_ms": 0,
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Erro ao executar compile check: {e}",
            "duration_ms": 0,
        }

    elapsed = round((time.time() - start) * 1000)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    errors = _extract_errors(combined)

    # Godot pode retornar exit code != 0 mesmo sem erros (ex: --quit), 
    # então o critério determinante é a presença de texto de erro.
    has_errors = len(errors) > 0

    # Mostra últimas linhas como contexto
    lines = combined.splitlines()
    context = lines[-30:] if len(lines) > 30 else lines

    return {
        "status": "failed" if has_errors else "passed",
        "exit_code": result.returncode,
        "duration_ms": elapsed,
        "errors": errors,
        "error_count": len(errors),
        "raw_tail": context,
    }


def _step_headless_run(proj: Path, godot: str, test_scene: str, headless_frames: int, timeout: int) -> dict:
    """Etapa 2: Executa o projeto em modo headless por N frames e captura saída."""
    start = time.time()

    try:
        result = subprocess.run(
            [godot, "--headless", "--path", str(proj), "--quit-after", str(headless_frames), test_scene],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        elapsed = round((time.time() - start) * 1000)
        # Captura output parcial emitido antes do timeout (Python 3.11+)
        partial_stdout = (e.stdout or b"").decode("utf-8", errors="replace") if e.stdout else ""
        partial_stderr = (e.stderr or b"").decode("utf-8", errors="replace") if e.stderr else ""
        return {
            "status": "failed",
            "error": f"Timeout ({timeout}s) na execucao headless. O jogo pode estar em loop infinito.",
            "duration_ms": elapsed,
            "crashed": False,
            "stacktrace": None,
            "exit_code": None,
            "stdout_last_2000": partial_stdout[-2000:] if partial_stdout else "",
            "stderr_last_2000": partial_stderr[-2000:] if partial_stderr else "",
        }
    except FileNotFoundError:
        return {
            "status": "failed",
            "error": f"Godot executavel nao encontrado: {godot}",
            "duration_ms": 0,
            "crashed": False,
            "stacktrace": None,
            "exit_code": None,
            "stdout_last_2000": "",
            "stderr_last_2000": "",
        }
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        return {
            "status": "failed",
            "error": f"Erro ao executar headless: {e}",
            "duration_ms": elapsed,
            "crashed": False,
            "stacktrace": None,
            "exit_code": None,
            "stdout_last_2000": "",
            "stderr_last_2000": "",
        }

    elapsed = round((time.time() - start) * 1000)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    
    crash_info = _detect_crash(combined, result.returncode)
    errors = _extract_errors(combined)

    return {
        "status": "failed" if crash_info["crashed"] or errors else "passed",
        "exit_code": result.returncode,
        "duration_ms": elapsed,
        "crashed": crash_info["crashed"],
        "stacktrace": crash_info["stacktrace"],
        "stdout_last_2000": (result.stdout or "")[-2000:],
        "stderr_last_2000": (result.stderr or "")[-2000:],
        "errors": errors,
    }


def _step_screenshot(
    proj: Path, godot: str, test_scene: str, headless_frames: int,
    timeout: int, screenshot_dir: str,
) -> dict:
    """Etapa 3: Captura screenshot após N frames de execução headless."""
    start = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Diretório de saída
    out_dir = Path(screenshot_dir) if screenshot_dir else (proj / "verification_screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Godot --write-movie gera frames numerados: <prefix>0001.png, <prefix>0002.png, ...
    movie_prefix = out_dir / f"verify_{timestamp}"

    startup = None
    if os.name == "nt":
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0  # SW_HIDE
    # NOTA: em Linux/Mac, startupinfo não existe e a janela do Godot
    # ficará visível durante o screenshot. Isso é uma limitação conhecida
    # (BUG-V03) — o MCP é primariamente Windows.

    cmd = [
        godot, "--path", str(proj),
        "--write-movie", str(movie_prefix) + ".png",
        "--fixed-fps", "60",
        "--quit-after", str(headless_frames),
        "--disable-vsync",
        "--resolution", "1280x720",
        test_scene,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
            startupinfo=startup,
            cwd=str(proj),
        )
    except subprocess.TimeoutExpired:
        elapsed = round((time.time() - start) * 1000)
        return {
            "status": "failed",
            "error": f"Timeout ({timeout}s) ao capturar screenshot.",
            "duration_ms": elapsed,
            "image_path": None,
            "image_base64": None,
        }
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        return {
            "status": "failed",
            "error": f"Erro ao capturar screenshot: {e}",
            "duration_ms": elapsed,
            "image_path": None,
            "image_base64": None,
        }

    elapsed = round((time.time() - start) * 1000)

    # Procura frames gerados: <movie_prefix>0001.png, <movie_prefix>0002.png, etc.
    frames = sorted(out_dir.glob(f"verify_{timestamp}*.png"))
    if not frames:
        # Tenta padrão alternativo: Godot pode ter gerado com outro formato
        frames = sorted(out_dir.glob(f"verify_{timestamp}*"))
        # Remove o prefixo sem frame (caso exista como dir)
        frames = [f for f in frames if f.is_file() and f.suffix.lower() == ".png"]

    if not frames:
        # Debug: log do stdout/stderr e listagem do diretório
        raw_output = (result.stdout or "") + "\n" + (result.stderr or "")
        dir_contents = [str(p.name) for p in out_dir.iterdir()] if out_dir.exists() else []
        return {
            "status": "failed",
            "error": "Nenhum frame PNG gerado pelo --write-movie.",
            "duration_ms": elapsed,
            "image_path": None,
            "image_base64": None,
            "debug_godot_output": raw_output[-2000:],
            "debug_dir_contents": dir_contents[-50:],
        }

    # Pega o último frame
    last_frame = frames[-1]
    try:
        img_data = last_frame.read_bytes()
        b64 = base64.b64encode(img_data).decode("ascii")

        # Copia para path canônico
        final_path = out_dir / f"verification_{timestamp}.png"
        if last_frame != final_path:
            import shutil
            shutil.copy2(str(last_frame), str(final_path))

        return {
            "status": "success",
            "image_path": str(final_path),
            "image_base64": b64,
            "image_size_bytes": len(img_data),
            "duration_ms": elapsed,
            "frame_count": len(frames),
            "headless_frames": headless_frames,
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Erro ao ler frame gerado: {e}",
            "duration_ms": elapsed,
            "image_path": str(last_frame),
            "image_base64": None,
        }


def _step_gut(proj: Path, godot: str, test_dir: str, timeout: int) -> dict:
    """Etapa 4: Executa suíte de testes GUT."""
    start = time.time()

    try:
        from tools.gut_ops import run_gut_tests as gut_run
        result = gut_run(
            project_path=str(proj),
            test_dir=test_dir,
            godot_path=godot,
            timeout=timeout,
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Erro ao invocar run_gut_tests: {e}",
            "duration_ms": round((time.time() - start) * 1000),
        }

    elapsed = round((time.time() - start) * 1000)
    # Não modifica o dict original — cria cópia com duration_ms
    result = dict(result)
    result["duration_ms"] = elapsed
    return result


def _step_audit_reachability(proj: Path, root_scene: str | None = None) -> dict:
    """Etapa 5: Auditoria de alcançabilidade de cenas."""
    start = time.time()

    try:
        from tools.audit_scene_reachability import audit_scene_reachability
        result = audit_scene_reachability(
            project_path=str(proj),
            root_scene=root_scene,
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Erro ao invocar audit_scene_reachability: {e}",
            "duration_ms": round((time.time() - start) * 1000),
        }

    elapsed = round((time.time() - start) * 1000)
    result = dict(result)
    result["duration_ms"] = elapsed
    result["unreachable_count"] = len(result.get("unreachable_scenes", []))
    return result


# ══════════════════════════════════════════════════════════════════════
# Pipeline Principal
# ══════════════════════════════════════════════════════════════════════

def _save_pipeline_result(result: dict) -> None:
    """Registra resultado do pipeline na maquina de fases (Feature 1 da Fase 1)."""
    try:
        from tools.phase_ops import _phase_state
        _phase_state.set_last_pipeline_result(result)
    except Exception:
        pass  # Falha no hook nao deve quebrar o pipeline


def run_verification_pipeline(
    project_path: str | None = None,
    godot_path: str | None = None,
    test_scene: str | None = None,
    gut_test_dir: str = "res://tests",
    headless_frames: int = 30,
    timeout_compile: int = 30,
    timeout_headless: int = 60,
    timeout_gut: int = 120,
    screenshot_dir: str | None = None,
    include_reachability_audit: bool = True,
    include_code_quality: bool = True,
) -> dict:
    """Executa pipeline de verificação completo em um projeto Godot.

    Etapas (executadas em sequência, com early exit na primeira falha):
      1. COMPILE CHECK  — força parse de todos os scripts (godot --headless --quit)
      2. HEADLESS RUN   — executa cena de teste, captura stdout/stderr/crash
      3. SCREENSHOT     — captura frame após N frames via --write-movie
      4. GUT TESTS      — roda suíte de testes unitários (opcional)
      5. REACHABILITY   — auditoria de cenas órfãs (opcional)
      6. CODE QUALITY   — gate gdtoolkit (gdlint + gdformat + gdradon) (Fatia 4.3, opcional)

    O pipeline PARA na primeira etapa que falhar (exceto GUT, que é opcional).
    Se test_scene não for fornecido e project.godot não definir run/main_scene,
    retorna status "ambiguous" solicitando a cena.

    Args:
        project_path: Caminho do projeto Godot. Se omitido, usa projeto ativo.
        godot_path: Caminho do executável Godot. Se omitido, auto-detecta.
        test_scene: Cena para rodar headless (ex: "res://scenes/main.tscn").
                    Se omitido, tenta ler run/main_scene do project.godot.
        gut_test_dir: Diretório de testes GUT (default: "res://tests").
        headless_frames: Quantos frames executar antes do screenshot (default: 30).
        timeout_compile: Timeout em segundos para compile check (default: 30).
        timeout_headless: Timeout em segundos para headless run (default: 60).
        timeout_gut: Timeout em segundos para GUT (default: 120).
        screenshot_dir: Diretório para screenshots. Default: <proj>/verification_screenshots/.
        include_reachability_audit: Se True, audita cenas órfãs (default: True).
        include_code_quality: Se True, roda gate gdtoolkit (default: True).
            Requer: pip install 'gdtoolkit>=4.0,<5.0'.

    Returns:
        dict com relatório consolidado JSON.
    """
    pipeline_start = time.time()
    steps = {}

    # ── Resolve paths ────────────────────────────────────────────
    proj = _resolve_project(project_path)
    if proj is None:
        return {
            "status": "error",
            "overall": "FALHOU",
            "error": "Nenhum projeto definido. Use set_active_project ou passe project_path.",
            "steps": {},
            "stopped_at_step": 0,
        }

    if not (proj / "project.godot").exists():
        return {
            "status": "error",
            "overall": "FALHOU",
            "error": f"project.godot nao encontrado em {proj}",
            "steps": {},
            "stopped_at_step": 0,
        }

    godot = _resolve_godot(godot_path)
    if screenshot_dir is None:
        screenshot_dir = str(proj / "verification_screenshots")

    # ── Resolve cena de teste ────────────────────────────────────
    scene = _resolve_test_scene(proj, test_scene)
    if scene is None:
        return {
            "status": "ambiguous",
            "overall": "CENA_NAO_DEFINIDA",
            "error": (
                "Nenhuma cena de teste definida. "
                "Passe o parametro 'test_scene' (ex: 'res://scenes/main.tscn') "
                "ou defina 'run/main_scene' no project.godot do projeto."
            ),
            "project_path": str(proj),
            "steps": {},
            "stopped_at_step": 0,
        }

    # ══════════════════════════════════════════════════════════════
    # ETAPA 1: COMPILE CHECK
    # ══════════════════════════════════════════════════════════════
    step1 = _step_compile(proj, godot, timeout_compile)
    steps["1_compile"] = step1

    if step1["status"] == "failed":
        elapsed_total = round((time.time() - pipeline_start) * 1000)
        result = {
            "status": "FALHOU",
            "overall": "FALHOU",
            "stopped_at_step": 1,
            "stopped_reason": f"Compile check falhou com {step1.get('error_count', 0)} erro(s).",
            "steps": steps,
            "total_duration_ms": elapsed_total,
            "project_path": str(proj),
            "test_scene": scene,
        }
        _save_pipeline_result(result)
        return result

    # ══════════════════════════════════════════════════════════════
    # ETAPA 2: HEADLESS RUN
    # ══════════════════════════════════════════════════════════════
    step2 = _step_headless_run(proj, godot, scene, headless_frames, timeout_headless)
    steps["2_headless_run"] = step2

    if step2["status"] == "failed":
        # Se crashou, etapa 3 é skipped
        steps["3_screenshot"] = {
            "status": "skipped_due_to_crash",
            "reason": "Etapa 2 (headless run) falhou — screenshot nao capturado.",
        }
        elapsed_total = round((time.time() - pipeline_start) * 1000)
        result = {
            "status": "FALHOU",
            "overall": "FALHOU",
            "stopped_at_step": 2,
            "stopped_reason": (
                f"Headless run {'crashou' if step2.get('crashed') else 'falhou'} "
                f"com exit code {step2.get('exit_code')}."
            ),
            "steps": steps,
            "total_duration_ms": elapsed_total,
            "project_path": str(proj),
            "test_scene": scene,
        }
        _save_pipeline_result(result)
        return result

    # ══════════════════════════════════════════════════════════════
    # ETAPA 3: SCREENSHOT (só se etapa 2 passou)
    # ══════════════════════════════════════════════════════════════
    step3 = _step_screenshot(
        proj, godot, scene, headless_frames,
        timeout=max(timeout_headless, 60),  # screenshot usa seu próprio timeout
        screenshot_dir=screenshot_dir,
    )
    steps["3_screenshot"] = step3
    # Screenshot não interrompe o pipeline — é informativo

    # ══════════════════════════════════════════════════════════════
    # ETAPA 4: GUT TESTS (opcional)
    # ══════════════════════════════════════════════════════════════
    step4 = _step_gut(proj, godot, gut_test_dir, timeout_gut)
    steps["4_gut_tests"] = step4

    # ══════════════════════════════════════════════════════════════
    # ETAPA 5: AUDITORIA DE ALCANÇABILIDADE (opcional)
    # ══════════════════════════════════════════════════════════════
    if include_reachability_audit:
        step5 = _step_audit_reachability(proj, scene)
        steps["5_audit_reachability"] = step5
    else:
        step5 = {"status": "skipped", "reason": "include_reachability_audit=False"}
        steps["5_audit_reachability"] = step5

    # ══════════════════════════════════════════════════════════════
    # ETAPA 6: CODE QUALITY GATE (gdtoolkit — Fatia 4.3)
    # ══════════════════════════════════════════════════════════════
    if include_code_quality and run_code_quality_gate is not None:
        step6 = run_code_quality_gate(str(proj))
        steps["6_code_quality"] = step6
    elif not include_code_quality:
        step6 = {"status": "skipped", "reason": "include_code_quality=False"}
        steps["6_code_quality"] = step6
    else:
        step6 = {
            "status": "skipped",
            "reason": "gdtoolkit não instalado. Instale com: pip install 'gdtoolkit>=4.0,<5.0'",
        }
        steps["6_code_quality"] = step6

    # ══════════════════════════════════════════════════════════════
    # RELATÓRIO CONSOLIDADO
    # ══════════════════════════════════════════════════════════════
    elapsed_total = round((time.time() - pipeline_start) * 1000)

    # Determina status geral
    # GUT skipped (sem testes) NÃO derruba o pipeline
    gut_has_failures = (
        step4.get("status") == "tests_failed"
        or (step4.get("results", {}).get("summary", {}).get("failed", 0) > 0)
    )

    compile_ok = step1["status"] == "passed"
    headless_ok = step2["status"] == "passed"
    screenshot_ok = step3["status"] == "success"
    gut_ok = step4.get("status") in ("success", "skipped") and not gut_has_failures
    reachability_ok = step5.get("status") in ("ok", "skipped", "issues_found")
    code_quality_ok = step6.get("gate_passed", True)  # True se skipped ou passou

    all_ok = compile_ok and headless_ok and gut_ok and reachability_ok and code_quality_ok
    # Screenshot não bloqueia (pode falhar por timeout/--write-movie)
    # mas reportamos no sumário

    # Sumário textual
    summary_parts = []
    summary_parts.append(f"Compile: {'PASS' if compile_ok else 'FAIL'} ({step1.get('error_count', 0)} erros)")
    summary_parts.append(f"Headless Run: {'PASS' if headless_ok else 'FAIL'}")
    summary_parts.append(f"Screenshot: {'OK' if screenshot_ok else step3.get('status', 'N/A')}")
    gut_label = step4.get("status", "?")
    if gut_label == "skipped":
        gut_label = "SKIPPED (sem testes)"
    elif gut_label == "success":
        gut_label = "PASS"
    elif gut_label == "tests_failed":
        gut_label = f"FAIL ({step4.get('results', {}).get('summary', {}).get('failed', '?')} falhas)"
    summary_parts.append(f"GUT: {gut_label}")
    if include_reachability_audit:
        u_count = step5.get("unreachable_count", 0)
        summary_parts.append(f"Alcancabilidade: {u_count} cenas orfas")
    if include_code_quality:
        cq_label = step6.get("summary", step6.get("status", "?"))
        summary_parts.append(f"Code Quality: {cq_label}")

    final_result = {
        "status": "PASSOU" if all_ok else "FALHOU",
        "overall": "PASSOU" if all_ok else "FALHOU",
        "stopped_at_step": None,
        "stopped_reason": None,
        "summary": " | ".join(summary_parts),
        "steps": steps,
        "total_duration_ms": elapsed_total,
        "project_path": str(proj),
        "test_scene": scene,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Hook: registra resultado na maquina de fases (Feature 1 da Fase 1)
    _save_pipeline_result(final_result)

    return final_result
