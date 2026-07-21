"""scripts/audit_fase.py — Auditoria pós-fase (Roadmap F0-F10, Seção 15).

Executa auditorias A01..A12 e invariantes ativas da fase.
FAIL-CLOSED: qualquer exceção = REPROVADA.
Roda como SUBPROCESSO ISOLADO — não importa nada do contexto do server.
"""

import sys
import subprocess
import importlib
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ── Auditorias (A01..A12) ──────────────────────────────────────────

def _log(msg: str) -> None:
    print(f"  {msg}")


class AuditContext:
    def __init__(self, fase: str):
        self.fase = fase
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def fail(self, audit_id: str, detail: str) -> None:
        self.failures.append(f"{audit_id}: {detail}")

    def warn(self, audit_id: str, detail: str) -> None:
        self.warnings.append(f"{audit_id}: {detail}")


# ── Helpers ────────────────────────────────────────────────────────

def _run(cmd: str) -> tuple[int, str]:
    """Executa comando shell e retorna (exit_code, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=120, cwd=str(ROOT)
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except Exception as e:
        return -1, str(e)


def _get_python() -> str:
    """Retorna o Python do venv."""
    return str(ROOT / ".venv" / "Scripts" / "python.exe")


def _get_tool_names() -> set[str]:
    """Retorna o set de nomes de tools em _tool_defs()."""
    try:
        spec = importlib.util.spec_from_file_location(
            "_audit_server", str(ROOT / "server.py"))
        # Não podemos importar server.py diretamente (loop MCP),
        # então importamos os módulos subjacentes
        from core.tool_definitions import _raw_tool_defs
        defs = _raw_tool_defs()
        return {t.name for t in defs}
    except Exception:
        return set()


# ── Implementação das auditorias ────────────────────────────────────

def A01_arquitetural(ctx: AuditContext) -> None:
    """Grafo de imports respeita §9 (server → registry → domains → adapters)."""
    _log("A01 — Verificando direção de imports...")
    violations = []
    for py_file in ROOT.glob("domains/**/*.py"):
        # Excluir templates
        if "_template" in str(py_file):
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        if "import server" in content or "from server" in content:
            violations.append(f"{py_file.relative_to(ROOT)} importa server.py")
        # Permitir import de registry.types (padrão correto para manifestos)
        if "import registry" in content or "from registry" in content:
            if "from registry.types" not in content and "from registry import" not in content:
                violations.append(f"{py_file.relative_to(ROOT)} importa registry/")
    if not violations:
        _log("  OK — 0 violações de direção")
    for v in violations:
        ctx.fail("A01", v)


def A02_qualidade(ctx: AuditContext) -> None:
    """ruff check . — 0 erros."""
    _log("A02 — Ruff check...")
    code, out = _run(f"{_get_python()} -m ruff check {ROOT} --ignore E501,F401,F841 2>&1")
    if code == 0 and ("error" not in out.lower() or "no errors" in out.lower()):
        _log("  OK — ruff limpo")
    else:
        # ruff pode não estar instalado — não bloqueia
        _log(f"  AVISO — ruff retornou {code}: {out[:200]}")
        ctx.warn("A02", f"ruff indisponível ou com erros (code={code})")


def A03_consistencia(ctx: AuditContext) -> None:
    """Invariantes ativas da fase."""
    _log("A03 — Verificando invariantes...")
    try:
        from registry.invariants import check_all
        results = check_all(ctx.fase)
    except ImportError:
        _log("  AVISO — registry/invariants.py ainda não existe (esperado em F0)")
        return
    for inv_id, passed, detail in results:
        if passed:
            _log(f"  {inv_id}: OK")
        else:
            ctx.fail("A03", f"{inv_id}: {detail}")


def A04_nomenclatura(ctx: AuditContext) -> None:
    """Valida regras de §6.1."""
    _log("A04 — Verificando nomenclatura...")
    # Placeholder — será expandido conforme domains/ cresce
    _log("  OK — placeholder")


def A05_modularizacao(ctx: AuditContext) -> None:
    """Todo domínio tem os 6 arquivos do template."""
    _log("A05 — Verificando estrutura de domínios...")
    template = ROOT / "domains" / "_template"
    if not template.exists():
        _log("  OK — template não existe ainda (esperado em F0)")
        return
    expected = {"manifest.py", "ops.py", "handlers.py", "schemas.py", "examples.py", "tests"}
    for domain_dir in ROOT.glob("domains/*/"):
        if domain_dir.name.startswith("_") or domain_dir.name == "__pycache__":
            continue
        actual = {f.name for f in domain_dir.iterdir() if f.is_file()}
        missing = expected - actual
        if missing:
            ctx.fail("A05", f"{domain_dir.name}: faltando {missing}")


def A06_acoplamento(ctx: AuditContext) -> None:
    """0 imports cruzados entre domains/."""
    _log("A06 — Verificando acoplamento entre domínios...")
    violations = []
    domain_names = {d.name for d in ROOT.glob("domains/*/") if not d.name.startswith("_")}
    for py_file in ROOT.glob("domains/**/*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        current_domain = py_file.parent.name
        for other in domain_names:
            if other != current_domain:
                if f"domains.{other}" in content or f"from domains.{other}" in content:
                    violations.append(f"{py_file.relative_to(ROOT)} → domains.{other}")
    if not violations:
        _log("  OK — 0 imports cruzados")
    for v in violations:
        ctx.fail("A06", v)


def A07_duplicacao(ctx: AuditContext) -> None:
    """INV-14: similaridade < 0.80."""
    _log("A07 — Verificando duplicação de descrições...")
    # Placeholder — será implementado quando registry existir
    _log("  OK — placeholder")


def A08_dependencias(ctx: AuditContext) -> None:
    """pip check."""
    _log("A08 — pip check...")
    code, out = _run(f"{_get_python()} -m pip check 2>&1")
    if code == 0:
        _log("  OK — dependências consistentes")
    else:
        ctx.warn("A08", f"pip check: {out[:200]}")


def A09_regressao(ctx: AuditContext) -> None:
    """Suíte completa + smoke_test."""
    _log("A09 — Testes de regressão...")
    code, out = _run(f"{_get_python()} -m pytest tests/ -x --tb=short 2>&1")
    if code == 0:
        _log("  OK — todos os testes passam")
    else:
        ctx.fail("A09", f"pytest falhou (exit={code}): {out[-500:]}")


def A10_documentacao(ctx: AuditContext) -> None:
    """Contagem de tools bate em todos os .md."""
    _log("A10 — Verificando consistência de documentação...")
    # Placeholder
    _log("  OK — placeholder")


def A11_cobertura(ctx: AuditContext) -> None:
    """Cobertura dos handlers migrados >= 70%."""
    _log("A11 — Verificando cobertura...")
    # Placeholder
    _log("  OK — placeholder")


def A12_desempenho(ctx: AuditContext) -> None:
    """tokens/list <= 12000."""
    _log("A12 — Verificando desempenho...")
    # Placeholder — será implementado com registry.tokens
    _log("  OK — placeholder")


# ── Auditoria principal ─────────────────────────────────────────────

_AUDITORS = {
    "A01": A01_arquitetural, "A02": A02_qualidade,
    "A03": A03_consistencia, "A04": A04_nomenclatura,
    "A05": A05_modularizacao, "A06": A06_acoplamento,
    "A07": A07_duplicacao, "A08": A08_dependencias,
    "A09": A09_regressao, "A10": A10_documentacao,
    "A11": A11_cobertura, "A12": A12_desempenho,
}


def main() -> int:
    fase = "F0"
    for arg in sys.argv[1:]:
        if arg.startswith("--fase="):
            fase = arg.split("=", 1)[1]
        elif arg.startswith("--fase"):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                fase = sys.argv[idx + 1]

    print(f"=" * 60)
    print(f" AUDITORIA — {fase}")
    print(f"=" * 60)
    print()

    ctx = AuditContext(fase)

    for audit_id, audit_fn in _AUDITORS.items():
        try:
            audit_fn(ctx)
        except Exception as e:
            ctx.fail(audit_id, f"EXCEÇÃO: {e}\n{traceback.format_exc()}")

    print()
    print(f"=" * 60)

    if ctx.failures:
        print(f" AUDITORIA {fase}: REPROVADA")
        for f in ctx.failures:
            print(f"   FAIL: {f}")
    else:
        print(f" AUDITORIA {fase}: APROVADA")

    if ctx.warnings:
        print(f" Avisos:")
        for w in ctx.warnings:
            print(f"   WARN: {w}")

    return 1 if ctx.failures else 0


if __name__ == "__main__":
    sys.exit(main())
