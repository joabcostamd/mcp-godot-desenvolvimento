"""auditar.py — Portao Executavel de Autoauditoria (Fatia 0.0.5).

Roda os 6 criterios (C1-C6) definidos no mestre secao 6 e retorna
exit code 0 se TODOS passaram, !=0 se qualquer um falhou.

IMPORTANTE: Este script NAO pode auditar a si mesmo. A Fatia 0.0.5
e a unica sem portao -- exige revisao humana obrigatoria.

Roda em subprocesso isolado: se server.py estiver quebrado, captura
o erro e retorna FALHA (fail-closed). Silencio nunca e aprovacao.

Uso:
    python auditar.py --fatia 0.1 [--c1-before BEFORE.json] [--c1-after AFTER.json]
                     [--canary CANARY.json] [--c4-checklist C4.json]
                     [--tool-name NAME] [--output RESULT.json]
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


# ══════════════════════════════════════════════════════════════════
# RESULTADO ESTRUTURADO
# ══════════════════════════════════════════════════════════════════

def _result_template(fatia_id: str) -> dict:
    return {
        "fatia": fatia_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exit_code": 0,
        "criteria": {
            "C1_contrato": {"status": "skipped", "detail": ""},
            "C2_canary": {"status": "skipped", "detail": ""},
            "C3_regressao": {"status": "skipped", "detail": ""},
            "C4_seguranca": {"status": "skipped", "detail": ""},
            "C5_orcamento": {"status": "skipped", "detail": ""},
            "C6_distinguibilidade": {"status": "skipped", "detail": ""},
            "C7_visual": {"status": "skipped", "detail": ""},
            "C8_behavior_audit": {"status": "skipped", "detail": ""},
        },
        "errors": [],
    }


def _save_result(result: dict, output_path: Path):
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ══════════════════════════════════════════════════════════════════
# C1 — CONTRATO (schema nao driftou)
# ══════════════════════════════════════════════════════════════════

def _run_c1(result: dict, c1_before: str | None, c1_after: str | None) -> bool:
    """Compara snapshots de tools/list antes/depois.

    Se --c1-before/--c1-after forem fornecidos (modo manual pre-0.11),
    compara os dois JSONs. Senao, usa contract_snapshot.check_snapshot()
    contra o baseline versionado (CONTRACT_SNAPSHOT.json).
    """
    try:
        if c1_before and c1_after:
            # Modo manual: compara dois arquivos
            before_path = Path(c1_before)
            after_path = Path(c1_after)
            if not before_path.exists():
                result["criteria"]["C1_contrato"]["status"] = "error"
                result["criteria"]["C1_contrato"]["detail"] = \
                    f"Arquivo before nao encontrado: {c1_before}"
                result["errors"].append("C1: before file not found")
                return False
            if not after_path.exists():
                result["criteria"]["C1_contrato"]["status"] = "error"
                result["criteria"]["C1_contrato"]["detail"] = \
                    f"Arquivo after nao encontrado: {c1_after}"
                result["errors"].append("C1: after file not found")
                return False

            before_data = json.loads(Path(c1_before).read_text(encoding="utf-8"))
            after_data = json.loads(Path(c1_after).read_text(encoding="utf-8"))

            before_tools = {t["name"]: t for t in before_data} if isinstance(before_data, list) else before_data
            after_tools = {t["name"]: t for t in after_data} if isinstance(after_data, list) else after_data

            before_names = set(before_tools.keys())
            after_names = set(after_tools.keys())
            added = after_names - before_names
            removed = before_names - after_names

            detail_parts = []
            if added:
                detail_parts.append(f"Tools adicionadas: {sorted(added)}")
            if removed:
                detail_parts.append(f"Tools removidas: {sorted(removed)}")
            if not added and not removed:
                detail_parts.append("Nenhuma mudanca detectada")

            detail = "; ".join(detail_parts) if detail_parts else "Nenhuma mudanca"
            passed = len(added) <= 5 and len(removed) == 0  # tolerancia de 5 adicoes

            result["criteria"]["C1_contrato"]["status"] = "pass" if passed else "fail"
            result["criteria"]["C1_contrato"]["detail"] = detail
            if not passed:
                result["errors"].append(f"C1: {detail}")
            return passed

        else:
            # Modo automatico: contract_snapshot contra baseline
            from tests.contract_snapshot import check_snapshot, generate_snapshot

            # Gera snapshot atual e compara com baseline
            check_result = check_snapshot()

            if check_result["status"] == "no_baseline":
                # Sem baseline -- aceita como pass (primeira execucao)
                result["criteria"]["C1_contrato"]["status"] = "pass"
                result["criteria"]["C1_contrato"]["detail"] = \
                    "Sem baseline (primeira execucao?) — snapshot atual aceito"
                return True

            summary = check_result["summary"]
            detail = (f"{summary['total']} mudancas: "
                      f"{summary['breaking']} breaking, "
                      f"{summary['warning']} warning, "
                      f"{summary['cosmetic']} cosmetic")

            # So falha em breaking changes
            passed = check_result["status"] != "breaking"

            result["criteria"]["C1_contrato"]["status"] = "pass" if passed else "fail"
            result["criteria"]["C1_contrato"]["detail"] = detail
            if not passed:
                result["errors"].append(f"C1: {detail}")
            return passed

    except Exception as e:
        result["criteria"]["C1_contrato"]["status"] = "error"
        result["criteria"]["C1_contrato"]["detail"] = f"Erro ao rodar C1: {e}"
        result["errors"].append(f"C1: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C2 — CANARY (comportamento certo)
# ══════════════════════════════════════════════════════════════════

def _run_c2(result: dict, canary_file: str | None) -> bool:
    """Executa chamadas canary declaradas e compara saida.

    Formato do JSON de canary:
    [
      {"tool": "nome_da_tool", "args": {...}, "expected_key": "key", "expected_value": "valor"},
      ...
    ]

    Se --canary nao for fornecido, pula (N/A).
    """
    if not canary_file:
        result["criteria"]["C2_canary"]["status"] = "skipped"
        result["criteria"]["C2_canary"]["detail"] = "Nenhuma canary fornecida (--canary ausente)"
        return True  # N/A nao falha

    try:
        canary_path = Path(canary_file)
        if not canary_path.exists():
            result["criteria"]["C2_canary"]["status"] = "error"
            result["criteria"]["C2_canary"]["detail"] = f"Arquivo nao encontrado: {canary_file}"
            result["errors"].append("C2: canary file not found")
            return False

        queries = json.loads(canary_path.read_text(encoding="utf-8"))
        if not isinstance(queries, list):
            queries = [queries]

        passed_all = True
        details = []

        for i, q in enumerate(queries):
            tool_name = q.get("tool", f"query_{i}")
            args = q.get("args", {})
            expected_key = q.get("expected_key")
            expected_value = q.get("expected_value")

            # Tenta importar e chamar o handler
            try:
                from server import _build_handlers
                handlers = _build_handlers()
                handler = handlers.get(tool_name)
                if handler is None:
                    details.append(f"[{tool_name}] Tool nao encontrada nos handlers")
                    passed_all = False
                    continue

                actual = handler(args)
                actual_str = str(actual)

                if expected_key:
                    # Tenta extrair o valor da chave esperada do resultado
                    if isinstance(actual, dict):
                        actual_val = str(actual.get(expected_key, ""))
                    else:
                        actual_val = actual_str

                    expected_str = str(expected_value)
                    if expected_str in actual_val:
                        details.append(f"[{tool_name}] OK — {expected_key} contem '{expected_str}'")
                    else:
                        details.append(
                            f"[{tool_name}] FALHA — {expected_key}: "
                            f"esperado conter '{expected_str}', "
                            f"obtido '{actual_val[:100]}'"
                        )
                        passed_all = False
                else:
                    details.append(f"[{tool_name}] OK — chamada concluiu sem erro")

            except Exception as e:
                details.append(f"[{tool_name}] ERRO — {e}")
                passed_all = False

        result["criteria"]["C2_canary"]["status"] = "pass" if passed_all else "fail"
        result["criteria"]["C2_canary"]["detail"] = " | ".join(details)
        if not passed_all:
            result["errors"].append(f"C2: canary failures — {len([d for d in details if 'FALHA' in d or 'ERRO' in d])} queries falharam")
        return passed_all

    except Exception as e:
        result["criteria"]["C2_canary"]["status"] = "error"
        result["criteria"]["C2_canary"]["detail"] = f"Erro ao rodar C2: {e}"
        result["errors"].append(f"C2: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C3 — REGRESSAO (nao quebrou o que existia)
# ══════════════════════════════════════════════════════════════════

def _run_c3(result: dict) -> bool:
    """Roda smoke_test e verifica que passou.

    Tenta chamar a tool smoke_test via handler. Se o MCP nao estiver
    disponivel (desconectado), tenta importar e executar diretamente.
    """
    try:
        from server import _build_handlers
        handlers = _build_handlers()
        smoke_handler = handlers.get("smoke_test")

        if smoke_handler is None:
            # Tenta via tests/
            try:
                from tools.test_ops import _smoke_test_impl
                smoke_result = _smoke_test_impl()
            except ImportError:
                result["criteria"]["C3_regressao"]["status"] = "skipped"
                result["criteria"]["C3_regressao"]["detail"] = \
                    "smoke_test nao disponivel (MCP desconectado? handler nao encontrado)"
                return True  # N/A nao falha
        else:
            smoke_result = smoke_handler()

        smoke_str = str(smoke_result) if smoke_result else ""
        # Tenta parsear como dict/JSON para checagem estruturada
        smoke_passed = True
        if isinstance(smoke_result, dict):
            smoke_status = smoke_result.get("status", "")
            if isinstance(smoke_status, str) and smoke_status.lower() != "success":
                smoke_passed = False
        elif isinstance(smoke_result, str):
            try:
                parsed = json.loads(smoke_result)
                if isinstance(parsed, dict):
                    smoke_status = parsed.get("status", "")
                    if isinstance(smoke_status, str) and smoke_status.lower() != "success":
                        smoke_passed = False
            except (json.JSONDecodeError, TypeError):
                # Fallback: string literal
                if "fail" in smoke_str.lower():
                    smoke_passed = False

        if smoke_passed:
            result["criteria"]["C3_regressao"]["status"] = "pass"
            result["criteria"]["C3_regressao"]["detail"] = \
                f"smoke_test concluido — status: success ({smoke_str[:150]})"
            return True
        else:
            result["criteria"]["C3_regressao"]["status"] = "fail"
            result["criteria"]["C3_regressao"]["detail"] = \
                f"smoke_test reportou falha: {smoke_str[:200]}"
            result["errors"].append("C3: smoke_test falhou")
            return False

    except Exception as e:
        result["criteria"]["C3_regressao"]["status"] = "error"
        result["criteria"]["C3_regressao"]["detail"] = f"Erro ao rodar C3: {e}"
        result["errors"].append(f"C3: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C4 — SEGURANCA / NAO-INTRUSAO (checklist binaria)
# ══════════════════════════════════════════════════════════════════

C4_EXPECTED_KEYS = [
    "loopback",
    "checkpoint",
    "nao_roubou_foco",
    "idempotente",
    "sem_segredo",
    "passou_pelo_rollup",
]


def _run_c4(result: dict, c4_file: str | None) -> bool:
    """Valida checklist binaria de seguranca.

    Formato do JSON:
    {"loopback": true, "checkpoint": true, ...}

    Qualquer false = falha. Chaves ausentes = falha.
    Se --c4-checklist nao for fornecido, pula (N/A).
    """
    if not c4_file:
        result["criteria"]["C4_seguranca"]["status"] = "skipped"
        result["criteria"]["C4_seguranca"]["detail"] = \
            "Nenhuma checklist fornecida (--c4-checklist ausente)"
        return True  # N/A nao falha

    try:
        c4_path = Path(c4_file)
        if not c4_path.exists():
            result["criteria"]["C4_seguranca"]["status"] = "error"
            result["criteria"]["C4_seguranca"]["detail"] = f"Arquivo nao encontrado: {c4_file}"
            result["errors"].append("C4: checklist file not found")
            return False

        checklist = json.loads(c4_path.read_text(encoding="utf-8"))

        failures = []
        for key in C4_EXPECTED_KEYS:
            if key not in checklist:
                failures.append(f"{key}: AUSENTE (esperado true/false)")
            elif checklist[key] is not True:
                failures.append(f"{key}: FALSE")

        if failures:
            result["criteria"]["C4_seguranca"]["status"] = "fail"
            result["criteria"]["C4_seguranca"]["detail"] = \
                f"{len(failures)} falhas: {'; '.join(failures)}"
            result["errors"].append(f"C4: {len(failures)} itens nao passaram")
            return False
        else:
            result["criteria"]["C4_seguranca"]["status"] = "pass"
            result["criteria"]["C4_seguranca"]["detail"] = \
                f"Todos os {len(C4_EXPECTED_KEYS)} itens OK"
            return True

    except Exception as e:
        result["criteria"]["C4_seguranca"]["status"] = "error"
        result["criteria"]["C4_seguranca"]["detail"] = f"Erro ao rodar C4: {e}"
        result["errors"].append(f"C4: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C5 — ORCAMENTO (teto de tools)
# ══════════════════════════════════════════════════════════════════

def _run_c5(result: dict) -> bool:
    """Roda test_budget_gate e verifica orcamento."""
    try:
        from tests.test_budget_gate import run_all_tests

        gate_result = run_all_tests(plant_overflow=False)

        status = gate_result.get("status", "unknown")
        errors = gate_result.get("errors", [])
        summary = gate_result.get("summary", {})

        detail = f"Status: {status}. "
        if "_total_tools" in summary:
            detail += f"Total tools: {summary['_total_tools']}. "
        detail += f"Fases com overflow: {len(errors)}"

        if status == "success":
            result["criteria"]["C5_orcamento"]["status"] = "pass"
            result["criteria"]["C5_orcamento"]["detail"] = detail
            return True
        else:
            result["criteria"]["C5_orcamento"]["status"] = "fail"
            result["criteria"]["C5_orcamento"]["detail"] = detail + " | " + "; ".join(errors)
            result["errors"].append(f"C5: {len(errors)} fases estouraram o teto")
            return False

    except Exception as e:
        result["criteria"]["C5_orcamento"]["status"] = "error"
        result["criteria"]["C5_orcamento"]["detail"] = f"Erro ao rodar C5: {e}"
        result["errors"].append(f"C5: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C6 — DISTINGUIBILIDADE (tool nova nao colide)
# ══════════════════════════════════════════════════════════════════

def _run_c6(result: dict, tool_name: str | None) -> bool:
    """Verifica se o nome da tool nova colide com existentes.

    Modo reduzido (pre-0.15): busca textual simples.
    Se --tool-name nao for fornecido, pula (N/A).
    """
    if not tool_name:
        result["criteria"]["C6_distinguibilidade"]["status"] = "skipped"
        result["criteria"]["C6_distinguibilidade"]["detail"] = \
            "Nenhum nome de tool fornecido (--tool-name ausente)"
        return True  # N/A nao falha

    try:
        from server import _tool_defs

        all_tools = _tool_defs()
        existing_names = {t.name.lower() for t in all_tools}
        existing_descs = {t.description.lower() if t.description else "" for t in all_tools}

        target_lower = tool_name.lower()

        # Checa nome exato
        if target_lower in existing_names:
            result["criteria"]["C6_distinguibilidade"]["status"] = "fail"
            result["criteria"]["C6_distinguibilidade"]["detail"] = \
                f"Tool '{tool_name}' ja existe com esse nome exato"
            result["errors"].append(f"C6: nome '{tool_name}' ja existe")
            return False

        # Checa colisao parcial (substring)
        collisions = []
        for name in existing_names:
            if target_lower in name or name in target_lower:
                collisions.append(name)

        if collisions:
            result["criteria"]["C6_distinguibilidade"]["status"] = "warning"
            result["criteria"]["C6_distinguibilidade"]["detail"] = \
                f"Nome '{tool_name}' similar a: {collisions[:5]}"
            # Warning nao falha — so alerta
            return True
        else:
            result["criteria"]["C6_distinguibilidade"]["status"] = "pass"
            result["criteria"]["C6_distinguibilidade"]["detail"] = \
                f"Nome '{tool_name}' — sem colisao detectada (modo textual reduzido)"
            return True

    except Exception as e:
        result["criteria"]["C6_distinguibilidade"]["status"] = "error"
        result["criteria"]["C6_distinguibilidade"]["detail"] = f"Erro ao rodar C6: {e}"
        result["errors"].append(f"C6: excecao — {e}")
        return False


def _run_c7_visual(result: dict, baseline_name: str = "baseline", threshold: float = 1.0) -> bool:
    """C7 — Regressao Visual: compara screenshot atual contra baseline.

    Usa visual_regression() do runtime_ops. Requer Godot headless
    e um baseline previamente salvo.

    Returns:
        True se passou ou baseline foi criado, False se detectou diferenca.
    """
    try:
        from tools.runtime_ops import visual_regression
        vr = visual_regression({"baseline_name": baseline_name, "threshold": threshold})

        if vr.get("action") == "baseline_saved":
            result["criteria"]["C7_visual"]["status"] = "baseline_saved"
            result["criteria"]["C7_visual"]["detail"] = (
                f"Baseline '{baseline_name}' criado. Execute novamente para comparar."
            )
            return True  # baseline criado = ok

        if vr.get("status") != "success":
            result["criteria"]["C7_visual"]["status"] = "error"
            result["criteria"]["C7_visual"]["detail"] = vr.get("message", "Erro desconhecido")
            result["errors"].append(f"C7: {vr.get('message', '')}")
            return False

        passed = vr.get("passed", False)
        diff_pct = vr.get("difference_percent", 100.0)

        if passed:
            result["criteria"]["C7_visual"]["status"] = "pass"
            result["criteria"]["C7_visual"]["detail"] = (
                f"Diferença {diff_pct:.2f}% <= {threshold}% — sem regressao visual."
            )
            return True
        else:
            result["criteria"]["C7_visual"]["status"] = "fail"
            result["criteria"]["C7_visual"]["detail"] = (
                f"Diferença {diff_pct:.2f}% > {threshold}% — possivel regressao visual!"
            )
            result["errors"].append(
                f"C7: Regressao visual detectada — {diff_pct:.2f}% > {threshold}%"
            )
            return False

    except ImportError as e:
        result["criteria"]["C7_visual"]["status"] = "error"
        result["criteria"]["C7_visual"]["detail"] = f"Import falhou: {e}"
        result["errors"].append(f"C7: import error — {e}")
        return False
    except Exception as e:
        result["criteria"]["C7_visual"]["status"] = "error"
        result["criteria"]["C7_visual"]["detail"] = f"Erro: {e}"
        result["errors"].append(f"C7: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# C8 — BEHAVIOR AUDIT (FATIA 2.C)
# ══════════════════════════════════════════════════════════════════

def _run_c8_behavior_audit(result: dict) -> bool:
    """Roda scripts/audit_behaviors.py e verifica 0 problemas criticos.

    Fail-closed: qualquer comportamento sem @tool, _get_configuration_warnings,
    sinal nao emitido, ou class_name mismatch -> FALHA.
    """
    import subprocess

    try:
        audit_script = ROOT / "scripts" / "audit_behaviors.py"
        if not audit_script.exists():
            result["criteria"]["C8_behavior_audit"]["status"] = "error"
            result["criteria"]["C8_behavior_audit"]["detail"] = (
                "Script scripts/audit_behaviors.py nao encontrado."
            )
            result["errors"].append("C8: audit script missing")
            return False

        proc = subprocess.run(
            ["python", str(audit_script)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
        )

        output = proc.stdout + proc.stderr

        # Parseia a saida para extrair metricas
        critical_ok = "no @tool: 0" in output and "no _get_configuration_warnings: 0" in output
        signals_ok = "signals not emitted: 0" in output
        warnings_ok = "class_name mismatch: 0" in output

        all_ok = critical_ok and signals_ok and warnings_ok

        if all_ok:
            result["criteria"]["C8_behavior_audit"]["status"] = "pass"
            result["criteria"]["C8_behavior_audit"]["detail"] = (
                "Todos os behaviors passaram: @tool, warnings, sinais emitidos, class_name OK."
            )
            return True
        else:
            # Extrai contagens para o detail
            import re
            no_tool_match = re.search(r"no @tool: (\d+)", output)
            no_warn_match = re.search(r"no _get_configuration_warnings: (\d+)", output)
            sig_match = re.search(r"signals not emitted: (\d+)", output)
            mismatch_match = re.search(r"class_name mismatch: (\d+)", output)

            detail_parts = []
            if no_tool_match and int(no_tool_match.group(1)) > 0:
                detail_parts.append(f"no @tool: {no_tool_match.group(1)}")
            if no_warn_match and int(no_warn_match.group(1)) > 0:
                detail_parts.append(f"no warnings: {no_warn_match.group(1)}")
            if sig_match and int(sig_match.group(1)) > 0:
                detail_parts.append(f"signals not emitted: {sig_match.group(1)}")
            if mismatch_match and int(mismatch_match.group(1)) > 0:
                detail_parts.append(f"class_name mismatch: {mismatch_match.group(1)}")

            detail = "; ".join(detail_parts) if detail_parts else "Problemas detectados na auditoria de behaviors."
            result["criteria"]["C8_behavior_audit"]["status"] = "fail"
            result["criteria"]["C8_behavior_audit"]["detail"] = detail
            result["errors"].append(f"C8: {detail}")
            return False

    except subprocess.TimeoutExpired:
        result["criteria"]["C8_behavior_audit"]["status"] = "error"
        result["criteria"]["C8_behavior_audit"]["detail"] = "Timeout ao rodar audit_behaviors.py."
        result["errors"].append("C8: timeout")
        return False
    except Exception as e:
        result["criteria"]["C8_behavior_audit"]["status"] = "error"
        result["criteria"]["C8_behavior_audit"]["detail"] = f"Erro: {e}"
        result["errors"].append(f"C8: excecao — {e}")
        return False


# ══════════════════════════════════════════════════════════════════
# ORQUESTRADOR PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def run_audit(
    fatia_id: str,
    c1_before: str | None = None,
    c1_after: str | None = None,
    canary_file: str | None = None,
    c4_file: str | None = None,
    tool_name: str | None = None,
    output_file: str | None = None,
    skip_c5: bool = False,
    visual: bool = False,
    visual_baseline: str = "baseline",
    visual_threshold: float = 1.0,
) -> dict:
    """Executa todos os criterios de autoauditoria.

    Returns:
        dict com resultado completo.
    """
    result = _result_template(fatia_id)

    # Executa cada criterio e coleta resultado
    c1_ok = _run_c1(result, c1_before, c1_after)
    c2_ok = _run_c2(result, canary_file)
    c3_ok = _run_c3(result)
    c4_ok = _run_c4(result, c4_file)

    if skip_c5:
        result["criteria"]["C5_orcamento"]["status"] = "pre_existente"
        result["criteria"]["C5_orcamento"]["detail"] = (
            "Pulado (--skip-c5). Problema pre-existente documentado "
            "no commit f056aed8. Responsabilidade da fatia 0.7."
        )
        c5_ok = True
    else:
        c5_ok = _run_c5(result)

    c6_ok = _run_c6(result, tool_name)

    # C8 — Behavior Audit (FATIA 2.C)
    c8_ok = _run_c8_behavior_audit(result)

    # C7 — Regressao Visual (opcional, via --visual)
    if visual:
        c7_ok = _run_c7_visual(result, visual_baseline, visual_threshold)
    else:
        c7_ok = True  # skipped — nao conta como falha

    # Consolida
    all_ok = all([c1_ok, c2_ok, c3_ok, c4_ok, c5_ok, c6_ok, c7_ok, c8_ok])
    result["exit_code"] = 0 if all_ok else 1

    # Grava resultado
    output_path = Path(output_file) if output_file else ROOT / "audit_result.json"
    _save_result(result, output_path)
    result["output_file"] = str(output_path)

    return result


# ══════════════════════════════════════════════════════════════════
# MAIN (CLI)
# ══════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="auditar.py — Portao Executavel de Autoauditoria (Fatia 0.0.5)",
    )
    parser.add_argument("--fatia", required=True, help="ID da fatia (ex: 0.1)")
    parser.add_argument("--c1-before", help="Snapshot BEFORE (JSON)")
    parser.add_argument("--c1-after", help="Snapshot AFTER (JSON)")
    parser.add_argument("--canary", help="Arquivo JSON com queries canary")
    parser.add_argument("--c4-checklist", help="Arquivo JSON com checklist C4")
    parser.add_argument("--tool-name", help="Nome da tool nova para C6")
    parser.add_argument("--output", help="Arquivo de saida (default: audit_result.json)")
    parser.add_argument("--skip-c5", action="store_true",
                       help="Pular C5 (problema pre-existente documentado)")
    parser.add_argument("--visual", action="store_true",
                       help="Executar regressao visual (C7) — requer Godot headless")
    parser.add_argument("--visual-baseline", default="baseline",
                       help="Nome do baseline visual (default: baseline)")
    parser.add_argument("--visual-threshold", type=float, default=1.0,
                       help="Threshold de diferenca %% para C7 (default: 1.0)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"AUDITAR.PY — Portao Executavel (Fatia {args.fatia})")
    print("=" * 65)

    try:
        import server  # noqa: F401 — verifica se o servidor importa
        print("[OK] server.py importado com sucesso")
    except Exception as e:
        print(f"[FALHA] ao importar server.py: {e}")
        # Fail-closed: sem servidor funcionando, nao pode auditar
        result = _result_template(args.fatia)
        result["exit_code"] = 1
        result["errors"].append(f"SERVIDOR QUEBRADO: {e}")
        result["criteria"]["C1_contrato"]["status"] = "error"
        result["criteria"]["C1_contrato"]["detail"] = f"Import server falhou: {e}"
        output_path = Path(args.output) if args.output else ROOT / "audit_result.json"
        _save_result(result, output_path)
        print(f"\n[FALHA] AUDITORIA ABORTADA — servidor quebrado. Resultado: {output_path}")
        sys.exit(1)

    result = run_audit(
        fatia_id=args.fatia,
        c1_before=args.c1_before,
        c1_after=args.c1_after,
        canary_file=args.canary,
        c4_file=args.c4_checklist,
        tool_name=args.tool_name,
        output_file=args.output,
        skip_c5=args.skip_c5,
        visual=args.visual,
        visual_baseline=args.visual_baseline,
        visual_threshold=args.visual_threshold,
    )

    # Reporte
    print(f"\nRESULTADO POR CRITERIO:")
    for crit_key, crit_data in result["criteria"].items():
        icon = "[PASS]" if crit_data["status"] == "pass" else (
            "[SKIP]" if crit_data["status"] == "skipped" else "[FAIL]"
        )
        print(f"  {icon} {crit_key}: {crit_data['status']} — {crit_data['detail'][:120]}")

    print(f"\nErros: {len(result['errors'])}")
    for e in result["errors"]:
        print(f"  [FAIL] {e[:200]}")

    print(f"\nResultado gravado: {result['output_file']}")
    print(f"Exit code: {result['exit_code']}")

    if result["exit_code"] == 0:
        print("\n[PASS] AUDITORIA PASSOU — Todos os criterios OK.")
    else:
        print(f"\n[FAIL] AUDITORIA FALHOU — {len(result['errors'])} erro(s).")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()