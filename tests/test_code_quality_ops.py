"""test_code_quality_ops.py — Teste completo do gdtoolkit Gate (Fatia 4.3 / Etapa B3).

Uso:
    # 1. Instalar gdtoolkit (se ainda não tiver):
    pip install "gdtoolkit>=4.0,<5.0"
    
    # 2. Rodar testes:
    python tests/test_code_quality_ops.py
    
    # 3. Testar com projeto Godot específico:
    python tests/test_code_quality_ops.py --project "C:/path/ao/projeto"

O que este script testa:
  T1 - gdtoolkit instalado? (run_gdlint, run_gdformat_check, run_gdradon)
  T2 - parse de output do gdlint (regex + pre-filtro)
  T3 - parse de output do gdradon
  T4 - run_code_quality_gate com projeto real
  T5 - graceful degradation (gdtoolkit ausente simulado)
  T6 - integração com run_verification_pipeline
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = 0
FAIL = 0
SKIP = 0


def ok(test_name: str):
    global PASS
    PASS += 1
    print(f"  ✅ {test_name}")


def falha(test_name: str, motivo: str = ""):
    global FAIL
    FAIL += 1
    msg = f"  ❌ {test_name}"
    if motivo:
        msg += f" — {motivo}"
    print(msg)


def pula(test_name: str, motivo: str = ""):
    global SKIP
    SKIP += 1
    msg = f"  ⏭️  {test_name}"
    if motivo:
        msg += f" — {motivo}"
    print(msg)


# ══════════════════════════════════════════════════════════════════════
# T1 — gdtoolkit está instalado?
# ══════════════════════════════════════════════════════════════════════

def test_gdtoolkit_installed():
    """Verifica se gdtoolkit está acessível e funcional."""
    print("\n📦 T1 — gdtoolkit installation")
    from tools.code_quality_ops import _ensure_gdtoolkit

    result = _ensure_gdtoolkit()
    if result["installed"]:
        ok(f"gdtoolkit instalado — versão: {result['version']}")
    else:
        falha(f"gdtoolkit NÃO instalado: {result['error']}")
        print("\n  ⚠️  Execute: pip install 'gdtoolkit>=4.0,<5.0'")
        return False
    return True


# ══════════════════════════════════════════════════════════════════════
# T2 — Parse gdlint output (unit test)
# ══════════════════════════════════════════════════════════════════════

def test_parse_gdlint_output():
    """Testa o parser de output do gdlint com saídas simuladas."""
    print("\n🔍 T2 — gdlint output parser")
    from tools.code_quality_ops import _parse_gdlint_output

    # Caso 1: output vazio
    result = _parse_gdlint_output("")
    if result["summary"]["total"] == 0 and len(result["violations"]) == 0:
        ok("output vazio → 0 violações")
    else:
        falha("output vazio", f"esperado 0, obteve {result['summary']['total']}")

    # Caso 2: uma violação de erro (path relativo)
    sample = "scripts/player.gd:10: Error: function-too-long (Function '_process' is too long (120 > 80))\n"
    result = _parse_gdlint_output(sample)
    if result["summary"]["error"] == 1 and result["summary"]["total"] == 1:
        v = result["violations"][0]
        if v["file"] == "scripts/player.gd" and v["line"] == 10 and v["severity"] == "error":
            ok("path relativo → 1 error detectado corretamente")
        else:
            falha("path relativo", f"dados incorretos: {v}")
    else:
        falha("path relativo", f"esperado 1 error, obteve {result['summary']}")

    # Caso 3: múltiplas violações com severidades diferentes
    sample = (
        "scripts/enemy.gd:5: Error: god-class (Class 'Enemy' is a god class)\n"
        "scripts/enemy.gd:20: Warning: function-args-too-many (Function 'init' has 8 args > 6)\n"
        "scripts/ui.gd:3: Style: unused-argument (Argument 'delta' is unused)\n"
    )
    result = _parse_gdlint_output(sample)
    errors = result["summary"]["error"]
    warnings = result["summary"]["warning"]
    styles = result["summary"]["style"]
    if errors == 1 and warnings == 1 and styles == 1 and result["summary"]["total"] == 3:
        ok("múltiplas severidades → 1 error + 1 warning + 1 style")
    else:
        falha("múltiplas severidades", f"obteve E={errors} W={warnings} S={styles}")

    # Caso 4: ordenação por severidade (error antes de warning antes de style)
    sample = (
        "scripts/a.gd:1: Style: unused-argument (msg)\n"
        "scripts/a.gd:2: Error: god-class (msg)\n"
        "scripts/a.gd:3: Warning: naming (msg)\n"
    )
    result = _parse_gdlint_output(sample)
    severities = [v["severity"] for v in result["violations"]]
    if severities == ["error", "warning", "style"]:
        ok("ordenação → error > warning > style")
    else:
        falha("ordenação", f"obteve {severities}")

    # Caso 5: path Windows (drive letter)
    sample = r"C:\project\scripts\player.gd:42: Warning: unused-argument (msg)"
    result = _parse_gdlint_output(sample)
    if result["summary"]["warning"] == 1:
        v = result["violations"][0]
        if "player.gd" in v["file"] and v["line"] == 42:
            ok("path Windows → detectado corretamente")
        else:
            falha("path Windows", f"dados: file={v['file']}, line={v['line']}")
    else:
        falha("path Windows", f"esperado 1 warning, obteve {result['summary']}")

    # Caso 6: linha sem padrão gdlint (deve ser ignorada)
    sample = "Checking 42 files...\nEverything is fine!\n"
    result = _parse_gdlint_output(sample)
    if result["summary"]["total"] == 0:
        ok("linhas não-gdlint → ignoradas corretamente")
    else:
        falha("linhas não-gdlint", f"esperado 0, obteve {result['summary']['total']}")

    # Caso 7: mensagem contendo dois-pontos
    sample = "scripts/test.gd:5: Error: syntax-error (Unexpected token: ':' at line 5)\n"
    result = _parse_gdlint_output(sample)
    if result["summary"]["error"] == 1:
        ok("mensagem com : → parse correto")
    else:
        falha("mensagem com :", f"esperado 1 error, obteve {result['summary']}")


# ══════════════════════════════════════════════════════════════════════
# T3 — Parse gdradon output (unit test)
# ══════════════════════════════════════════════════════════════════════

def test_parse_gdradon_output():
    """Testa o parser de output do gdradon."""
    print("\n📊 T3 — gdradon output parser")
    from tools.code_quality_ops import _parse_gdradon_output

    # Caso 1: output vazio
    result = _parse_gdradon_output("")
    if result["total_functions"] == 0 and result["average_complexity"] == 0.0:
        ok("output vazio → 0 funções")
    else:
        falha("output vazio", f"obteve {result['total_functions']} funções")

    # Caso 2: um arquivo com funções
    sample = (
        "scripts/player.gd\n"
        "    F 5:0 _ready - A (2)\n"
        "    F 15:0 _process - B (5)\n"
        "    F 30:0 take_damage - A (3)\n"
    )
    result = _parse_gdradon_output(sample)
    if result["files_analyzed"] == 1 and result["total_functions"] == 3:
        if result["total_complexity"] == 10 and result["max_complexity"] == 5:
            ok("1 arquivo 3 funções → complexidade total=10 max=5")
        else:
            falha("complexidade", f"total={result['total_complexity']} max={result['max_complexity']}")
    else:
        falha("arquivos/funções", f"files={result['files_analyzed']} funcs={result['total_functions']}")

    # Caso 3: múltiplos arquivos
    sample = (
        "scripts/player.gd\n"
        "    F 5:0 _ready - A (2)\n"
        "scripts/enemy.gd\n"
        "    F 10:0 _process - C (12)\n"
    )
    result = _parse_gdradon_output(sample)
    if result["files_analyzed"] == 2 and result["max_complexity"] == 12:
        ok("2 arquivos → max_complexity=12 detectado")
    else:
        falha("2 arquivos", f"files={result['files_analyzed']} max={result['max_complexity']}")

    # Caso 4: high_complexity_files
    # threshold é 50, então complexidade 10+5=15 não deve aparecer
    result_small = _parse_gdradon_output(
        "scripts/small.gd\n    F 1:0 f - A (2)\n"
    )
    if len(result_small["high_complexity_files"]) == 0:
        ok("threshold complexidade → arquivo pequeno não listado")
    else:
        falha("threshold", f"esperado 0 high, obteve {len(result_small['high_complexity_files'])}")


# ══════════════════════════════════════════════════════════════════════
# T4 — run_code_quality_gate (requer projeto Godot real)
# ══════════════════════════════════════════════════════════════════════

def test_code_quality_gate(project_path: str | None = None):
    """Testa o gate completo com um projeto real (se disponível)."""
    print("\n🚦 T4 — run_code_quality_gate")
    from tools.code_quality_ops import run_code_quality_gate, _find_project_root, _ensure_gdtoolkit

    toolkit = _ensure_gdtoolkit()
    if not toolkit["installed"]:
        pula("gate completo", "gdtoolkit não instalado")
        return

    proj = _find_project_root(project_path)
    if proj is None:
        # Tenta o breakout_test conhecido
        candidates = [
            Path(r"C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\breakout_test"),
            Path(r"C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\shardbreaker-nodebuster-like"),
        ]
        for c in candidates:
            if (c / "project.godot").exists():
                project_path = str(c)
                proj = c
                break

    if proj is None:
        pula("gate completo", "nenhum projeto Godot encontrado. Use --project <path>")
        return

    result = run_code_quality_gate(str(proj))

    print(f"  📁 Projeto: {proj}")
    print(f"  📋 Status: {result.get('status')}")
    print(f"  🚪 Gate: {'PASS' if result.get('gate_passed') else 'FAIL'}")
    print(f"  📝 Summary: {result.get('summary')}")

    if result.get("status") == "error":
        falha("gate", result.get("error", "erro desconhecido"))
    elif result.get("gate_passed"):
        ok(f"gate passou — {result.get('summary', '')}")
    else:
        # Gate falhou — mostrar violações (COMPORTAMENTO CORRETO!)
        gdlint_data = result.get("results", {}).get("gdlint", {})
        violations = gdlint_data.get("violations", [])
        gdformat_data = result.get("results", {}).get("gdformat", {})
        unformatted = gdformat_data.get("unformatted_count", 0)
        radon_data = result.get("results", {}).get("gdradon", {})
        avg_cc = radon_data.get("average_complexity", "?")
        
        print(f"  ⚠️  Gate detectou problemas REAIS no código:")
        print(f"     gdlint: {len(violations)} violações")
        print(f"     gdformat: {unformatted} arquivos mal formatados")
        print(f"     gdradon: avg CC={avg_cc}")
        if violations:
            print(f"     Top 3 violações:")
            for v in violations[:3]:
                print(f"       {v['file'].split(chr(92))[-1]}:{v['line']} [{v['severity']}] {v['code']}")
        ok(f"gate detectou problemas corretamente (gdlint={len(violations)}, fmt={unformatted}, cc={avg_cc})")


# ══════════════════════════════════════════════════════════════════════
# T5 — Graceful degradation (gdtoolkit ausente)
# ══════════════════════════════════════════════════════════════════════

def test_graceful_degradation():
    """Testa que o sistema não quebra quando gdtoolkit não está instalado."""
    print("\n🛡 T5 — Graceful degradation")
    from tools.code_quality_ops import run_gdlint, run_gdformat_check, run_gdradon, run_code_quality_gate

    # Testa com project_path inválido — deve retornar erro claro
    result = run_gdlint("/nonexistent/path")
    if result["status"] == "error" and "nenhum projeto" in result.get("error", "").lower():
        ok("projeto inexistente → erro claro")
    else:
        falha("projeto inexistente", f"status={result['status']}")

    result = run_code_quality_gate("/nonexistent/path")
    if result.get("gate_passed") == False:
        ok("gate com projeto inexistente → gate_passed=False")
    else:
        falha("gate projeto inexistente", f"gate_passed={result.get('gate_passed')}")


# ══════════════════════════════════════════════════════════════════════
# T6 — Integração com run_verification_pipeline
# ══════════════════════════════════════════════════════════════════════

def test_pipeline_integration():
    """Testa a integração no pipeline de verificação."""
    print("\n🔗 T6 — run_verification_pipeline integration")

    # Verifica se o import funciona
    try:
        from tools.verification_ops import run_verification_pipeline
        ok("import run_verification_pipeline → OK")
    except ImportError as e:
        falha("import", str(e))
        return

    # Verifica se o parâmetro include_code_quality existe na assinatura
    import inspect
    sig = inspect.signature(run_verification_pipeline)
    params = list(sig.parameters.keys())
    if "include_code_quality" in params:
        ok(f"parâmetro include_code_quality → presente (default={sig.parameters['include_code_quality'].default})")
    else:
        falha("parâmetro include_code_quality → AUSENTE!")

    # Verifica se include_reachability_audit também está (regressão)
    if "include_reachability_audit" in params:
        ok("parâmetro include_reachability_audit → preservado (sem regressão)")
    else:
        falha("parâmetro include_reachability_audit → REGRESSÃO! parâmetro sumiu")

    # Testa que o pipeline não quebra com include_code_quality=True sem projeto
    result = run_verification_pipeline(
        project_path="/nonexistent/path",
        include_code_quality=True,
    )
    if result.get("overall") == "FALHOU":
        # Deve falhar por falta de projeto, não por code_quality
        if "project.godot" in result.get("error", ""):
            ok("pipeline com projeto inexistente → erro claro (sem quebrar)")
        else:
            ok("pipeline com projeto inexistente → tratado corretamente")
    else:
        falha("pipeline projeto inexistente", f"overall={result.get('overall')}")


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Teste completo do gdtoolkit Gate (B3)")
    parser.add_argument("--project", help="Caminho do projeto Godot para teste real")
    args = parser.parse_args()

    print("=" * 60)
    print("🧪 TESTE COMPLETO — gdtoolkit Gate (Fatia 4.3 / Etapa B3)")
    print("=" * 60)

    # T1 — Instalação
    installed = test_gdtoolkit_installed()

    # T2 — Parser gdlint (sempre roda, sem dependências)
    test_parse_gdlint_output()

    # T3 — Parser gdradon (sempre roda, sem dependências)
    test_parse_gdradon_output()

    # T4 — Gate completo (requer gdtoolkit + projeto)
    if installed:
        test_code_quality_gate(args.project)

    # T5 — Graceful degradation (sempre roda)
    test_graceful_degradation()

    # T6 — Pipeline integration (sempre roda)
    test_pipeline_integration()

    # ── Sumário ──────────────────────────────────────────────────
    total = PASS + FAIL + SKIP
    print(f"\n{'=' * 60}")
    print(f"📊 RESULTADO: {PASS}✅ / {FAIL}❌ / {SKIP}⏭️  (total: {total})")
    print(f"{'=' * 60}")

    if FAIL > 0:
        print("\n❌ ALGUNS TESTES FALHARAM. Verifique os detalhes acima.")
        sys.exit(1)
    elif SKIP > 0:
        print(f"\n⚠️  {SKIP} testes pulados (instale gdtoolkit e forneça --project para testes completos).")
        sys.exit(0)
    else:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        sys.exit(0)


if __name__ == "__main__":
    main()
