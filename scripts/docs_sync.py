"""docs_sync.py — Sincroniza números reais do código nos documentos.

Executar: python scripts/docs_sync.py
Idempotente: rodar 2x não muda nada.

Substitui marcadores <!--DOCS_SYNC:key-->valor<!--/DOCS_SYNC-->
nos documentos. O valor é SEMPRE lido do código — nunca digitado à mão.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _safe_count_tools() -> int:
    """Conta tools sem efeitos colaterais (import bloqueante)."""
    import server
    return len(server._raw_tool_defs())


def _safe_count_handlers() -> int:
    """Conta handlers sem efeitos colaterais."""
    import server
    return len(server._build_handlers())


def _safe_count_rollups() -> int:
    """Conta rollups registrados."""
    try:
        from tools.rollups import get_rollup_handlers
        return len(get_rollup_handlers())
    except Exception:
        return 0


def _get_version() -> str:
    """Lê versão do pyproject.toml."""
    ppt = ROOT / "pyproject.toml"
    if ppt.exists():
        text = ppt.read_text(encoding="utf-8")
        m = re.search(r'version\s*=\s*"([^"]+)"', text)
        if m:
            return m.group(1)
    return "0.0.0"


def _get_mcp_version() -> str:
    """Lê versão do server.py (fallback)."""
    sp = ROOT / "server.py"
    text = sp.read_text(encoding="utf-8")
    m = re.search(r'version\s*=\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    return "0.0.0"


def sync_file(filepath: str, values: dict[str, str]) -> bool:
    """Sincroniza marcadores DOCS_SYNC num arquivo.

    Formato: <!--DOCS_SYNC:key-->valor<!--/DOCS_SYNC-->
    """
    p = ROOT / filepath
    if not p.exists():
        return False

    content = p.read_text(encoding="utf-8")
    changed = False

    for key, new_value in values.items():
        pattern = rf'(<!--DOCS_SYNC:{key}-->)(.*?)(<!--/DOCS_SYNC:{key}-->)'

        match = re.search(pattern, content)
        if match:
            old_full = match.group(0)
            new_full = match.group(1) + new_value + match.group(3)
            if old_full != new_full:
                content = content.replace(old_full, new_full)
                changed = True
        else:
            # Marcador não existe — pular (não adicionar automaticamente)
            pass

    if changed:
        p.write_text(content, encoding="utf-8")

    return changed


def main() -> int:
    tools = _safe_count_tools()
    handlers = _safe_count_handlers()
    rollups = _safe_count_rollups()
    version = _get_version() or _get_mcp_version()

    values = {
        "tools": str(tools),
        "handlers": str(handlers),
        "rollups": str(rollups),
        "version": version,
    }

    print(f"📊 docs_sync — {version}")
    print(f"   tools:    {tools}")
    print(f"   handlers: {handlers}")
    print(f"   rollups:  {rollups}")
    print()

    # Sincronizar README.md
    changed = False
    for doc in ["README.md"]:
        if sync_file(doc, values):
            print(f"✅ {doc} atualizado")
            changed = True
        else:
            marcadores = sum(1 for v in values if f"DOCS_SYNC:{v}" in (ROOT / doc).read_text(encoding="utf-8"))
            if marcadores > 0:
                print(f"✓  {doc} já atualizado ({marcadores} marcadores)")
            else:
                print(f"⚠️  {doc}: sem marcadores DOCS_SYNC (pulado)")

    if not changed:
        print("\n✅ Idempotente — nenhuma mudança necessária.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
