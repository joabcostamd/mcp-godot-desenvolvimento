"""contract_snapshot.py — Contract Snapshot + Diff (Fatia 0.11).

Gera e verifica snapshot de tools/list para detectar drift de schema.
Usado pelo CI como gate e pela autoauditoria como critério C1.

Uso:
    python tests/contract_snapshot.py --generate   # cria CONTRACT_SNAPSHOT.json
    python tests/contract_snapshot.py --check     # compara contra baseline (default)
    python tests/contract_snapshot.py --check --ignore-tool PREFIX  # ignora tools c/ prefixo
"""

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "CONTRACT_SNAPSHOT.json"

# ── Severidades ──────────────────────────────────────────────────────
SEVERITY_BREAKING = "breaking"
SEVERITY_WARNING = "warning"
SEVERITY_COSMETIC = "cosmetic"


def load_server_tools() -> dict[str, Any]:
    """Carrega as ferramentas atuais do servidor MCP."""
    sys.path.insert(0, str(ROOT))
    import server
    return {t.name: _serialize_tool(t) for t in server._tool_defs()}


def _serialize_tool(tool) -> dict:
    """Serializa uma tool para formato de snapshot (canônico)."""
    return {
        "description": (tool.description or "").strip(),
        "inputSchema": _canonical_schema(tool.inputSchema),
    }


def _canonical_schema(schema: Any) -> Any:
    """Retorna schema em formato canônico (sort_keys)."""
    if isinstance(schema, dict):
        return json.loads(json.dumps(schema, sort_keys=True, ensure_ascii=False))
    return schema


def compute_hash(tools: dict[str, Any]) -> str:
    """Calcula SHA-256 do conteúdo canônico de tools (sem metadados)."""
    raw = json.dumps(tools, sort_keys=True, ensure_ascii=False, indent=2)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_snapshot() -> dict:
    """Gera snapshot completo do estado atual das tools."""
    tools = load_server_tools()
    return {
        "hash": compute_hash(tools),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_count": len(tools),
        "tools": tools,
    }


def save_snapshot(snapshot: dict) -> Path:
    """Salva snapshot em disco."""
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, sort_keys=True, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return SNAPSHOT_PATH


def load_baseline() -> dict | None:
    """Carrega snapshot baseline do disco."""
    if not SNAPSHOT_PATH.exists():
        return None
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def classify_changes(baseline_tools: dict, current_tools: dict,
                     ignore_tools: set[str] | None = None) -> list[dict]:
    """Classifica mudanças entre baseline e estado atual.

    Returns:
        Lista de dicts: {tool, change, severity, detail}
    """
    changes = []
    ignore_tools = ignore_tools or set()

    baseline_names = set(baseline_tools.keys()) - ignore_tools
    current_names = set(current_tools.keys()) - ignore_tools

    # Tools removidas (breaking)
    removed = baseline_names - current_names
    for name in sorted(removed):
        changes.append({
            "tool": name,
            "change": "removida",
            "severity": SEVERITY_BREAKING,
            "detail": f"Tool '{name}' não está mais em _tool_defs()",
        })

    # Tools adicionadas (warning)
    added = current_names - baseline_names
    for name in sorted(added):
        changes.append({
            "tool": name,
            "change": "adicionada",
            "severity": SEVERITY_WARNING,
            "detail": f"Nova tool '{name}' adicionada",
        })

    # Tools que existem em ambos (analisar diferenças)
    common = baseline_names & current_names
    for name in sorted(common):
        bl = baseline_tools[name]
        cur = current_tools[name]

        # Descrição mudou
        if bl.get("description") != cur.get("description"):
            changes.append({
                "tool": name,
                "change": "descricao_alterada",
                "severity": SEVERITY_WARNING,
                "detail": (
                    f"Descrição de '{name}' mudou:\n"
                    f"  ANTES: {bl.get('description', '')[:100]}\n"
                    f"  DEPOIS: {cur.get('description', '')[:100]}"
                ),
            })

        # Schema mudou
        bl_schema = json.dumps(bl.get("inputSchema", {}), sort_keys=True)
        cur_schema = json.dumps(cur.get("inputSchema", {}), sort_keys=True)
        if bl_schema != cur_schema:
            severity = _classify_schema_change(
                bl.get("inputSchema", {}), cur.get("inputSchema", {})
            )
            changes.append({
                "tool": name,
                "change": "schema_alterado",
                "severity": severity,
                "detail": f"inputSchema de '{name}' mudou (severidade: {severity})",
            })

    return changes


def _classify_schema_change(old: dict, new: dict) -> str:
    """Classifica severidade de mudança de schema.

    breaking: param obrigatório novo, tipo restringido
    warning: param opcional novo, tipo estendido, required reduzido
    cosmetic: só ordem/whitespace
    """
    old_required = set(old.get("required", []))
    new_required = set(new.get("required", []))

    old_props = set(old.get("properties", {}).keys())
    new_props = set(new.get("properties", {}).keys())

    # Parâmetro tornou-se obrigatório (breaking)
    if new_required - old_required:
        return SEVERITY_BREAKING

    # Parâmetro removido de required (warning — mais permissivo)
    if old_required - new_required:
        return SEVERITY_WARNING

    # Parâmetro novo (warning)
    if new_props - old_props:
        return SEVERITY_WARNING

    # Parâmetro removido (breaking — cliente pode fornecer algo que não existe mais)
    if old_props - new_props:
        return SEVERITY_WARNING

    # Só cosmetic
    return SEVERITY_COSMETIC


def check_snapshot(ignore_tools: set[str] | None = None) -> dict:
    """Verifica snapshot atual contra baseline.

    Returns:
        dict com status, changes, summary.
    """
    baseline = load_baseline()
    if baseline is None:
        return {
            "status": "no_baseline",
            "message": "Baseline não encontrado. Rode --generate primeiro.",
            "changes": [],
            "summary": {},
        }

    current_tools = load_server_tools()
    baseline_tools = baseline.get("tools", {})
    changes = classify_changes(baseline_tools, current_tools, ignore_tools)

    # Contagem por severidade
    breaking = [c for c in changes if c["severity"] == SEVERITY_BREAKING]
    warnings = [c for c in changes if c["severity"] == SEVERITY_WARNING]
    cosmetic = [c for c in changes if c["severity"] == SEVERITY_COSMETIC]

    # Hashes: recalcula ambos a partir dos dicionários reais
    baseline_hash = compute_hash(baseline_tools)
    current_hash = compute_hash(current_tools)

    status = "ok"
    if breaking:
        status = "breaking"
    elif warnings:
        status = "warning"

    return {
        "status": status,
        "baseline_hash": baseline.get("hash", ""),
        "current_hash": current_hash,
        "hash_match": baseline_hash == current_hash,
        "baseline_tool_count": len(baseline_tools),
        "current_tool_count": len(current_tools),
        "changes": changes,
        "summary": {
            "total": len(changes),
            "breaking": len(breaking),
            "warning": len(warnings),
            "cosmetic": len(cosmetic),
        },
    }


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--ignore-tool=")]
    ignore_tool_prefixes = {
        a.split("=", 1)[1]
        for a in sys.argv[1:]
        if a.startswith("--ignore-tool=")
    }

    generate_mode = "--generate" in args

    if generate_mode:
        print("📸 Gerando snapshot de contrato...")
        snapshot = generate_snapshot()
        path = save_snapshot(snapshot)
        print(f"✅ Snapshot salvo em: {path.name}")
        print(f"   Tools: {snapshot['tool_count']}")
        print(f"   Hash:  {snapshot['hash'][:16]}...")
        return 0

    # Default: --check
    result = check_snapshot(ignore_tool_prefixes)

    print("=" * 65)
    print("🔍 CONTRACT SNAPSHOT CHECK (Fatia 0.11)")
    print("=" * 65)

    print(f"\n📊 Baseline:  {result['baseline_tool_count']} tools, hash {result.get('baseline_hash', '?')[:16]}...")
    print(f"📊 Atual:     {result['current_tool_count']} tools, hash {result.get('current_hash', '?')[:16]}...")

    if result["hash_match"]:
        print("\n✅ Snapshot IDÊNTICO ao baseline — nenhuma mudança de contrato.")
        return 0

    print(f"\n⚠️ O snapshot DIFERE do baseline ({result['summary']['total']} mudanças):")
    for c in result["changes"]:
        icon = "🔴" if c["severity"] == "breaking" else ("🟡" if c["severity"] == "warning" else "⚪")
        print(f"  {icon} [{c['severity']}] {c['tool']}: {c['change']}")

    print(f"\n📋 Resumo: {result['summary']['total']} mudanças "
          f"({result['summary']['breaking']} breaking, "
          f"{result['summary']['warning']} warning, "
          f"{result['summary']['cosmetic']} cosmetic)")

    if result["status"] == "breaking":
        print("\n❌ BREAKING CHANGE DETECTADA — O CI falhará.")
        return 2
    elif result["status"] == "warning":
        print("\n🟡 WARNING — Mudança não-breaking, mas revisão recomendada.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())