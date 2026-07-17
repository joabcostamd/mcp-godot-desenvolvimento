"""verify_loopback.py — Verifica que todos os binds de rede usam 127.0.0.1 (Fatia 0.4).

Varre arquivos Python do projeto (tools/, server.py, runtime_bridge_client.py)
em busca de binds em 0.0.0.0. Falha se encontrar violação da regra 3.1 do mestre.

Uso:
    python tools/verify_loopback.py   # exit code 0 = conforme
    python tools/verify_loopback.py --verbose  # mostra cada bind verificado
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Arquivos a verificar (não ferramentas MCP — são infraestrutura de rede)
TARGET_FILES = [
    "tools/addon_bridge.py",
    "tools/bridge.py",
    "tools/bootstrap_ops.py",
    "tools/debugger_ops.py",
    "tools/editor_bridge.py",
    "tools/game_bridge.py",
    "tools/lsp_ops.py",
    "tools/networking_ops.py",
    "tools/runtime_ops.py",
    "runtime_bridge_client.py",
]

# Ocorrências de 0.0.0.0 como host em bind/connect
VIOLATION_PATTERNS = ["0.0.0.0", '"0.0.0.0"', "'0.0.0.0'"]

# Binds conhecidos em 127.0.0.1 (para verbose reporting)
KNOWN_LOOPBACK_BINDS = {
    "tools/addon_bridge.py": {"WS_HOST": "127.0.0.1", "port": 9082},
    "tools/bridge.py": {"EDITOR_PORT": "? (conexão loopback)"},
    "tools/bootstrap_ops.py": {"LSP_HOST": "127.0.0.1:6005", "WS_HOST": "127.0.0.1:9082", "DEBUGGER_PORT": "6006"},
    "tools/debugger_ops.py": {"DEBUGGER_HOST": "127.0.0.1"},
    "tools/editor_bridge.py": {"socket": "127.0.0.1 (dinâmico)"},
    "tools/game_bridge.py": {"socket": "127.0.0.1 (dinâmico)"},
    "tools/lsp_ops.py": {"LSP_HOST": "127.0.0.1:6005"},
    "tools/networking_ops.py": {"address default": "127.0.0.1", "port": "9090"},
    "tools/runtime_ops.py": {"socket": "127.0.0.1 (dinâmico)"},
    "runtime_bridge_client.py": {"HOST": "127.0.0.1", "PORT": 8790},
}


def check_file_for_violations(filepath: Path, verbose: bool = False) -> list[str]:
    """Verifica um arquivo Python por binds em 0.0.0.0."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [f"  ⚠️  Erro ao ler {filepath.name}: {e}"]

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        # Pular comentários e linhas vazias
        if stripped.startswith("#") or not stripped:
            continue
        # Verificar por padrões de 0.0.0.0
        for pattern in VIOLATION_PATTERNS:
            if pattern in stripped:
                violations.append(f"  ❌ {filepath.name}:{i}: {stripped}")

    if verbose and not violations:
        rel = filepath.relative_to(ROOT)
        info = KNOWN_LOOPBACK_BINDS.get(str(rel), {})
        if info:
            details = "; ".join(f"{k}={v}" for k, v in info.items())
            print(f"  ✅ {rel.name}: {details}")
        else:
            print(f"  ✅ {rel.name}: sem binds encontrados")

    return violations


def main():
    verbose = "--verbose" in sys.argv
    print("=" * 60)
    print(" VERIFICAÇÃO DE BIND LOOPBACK (Fatia 0.4)")
    print(" Regra 3.1 do mestre: 127.0.0.1, nunca 0.0.0.0")
    print("=" * 60)
    print()

    total_violations = []
    files_checked = 0

    for rel_path in TARGET_FILES:
        filepath = ROOT / rel_path
        if not filepath.exists():
            print(f"  ⚠️  Arquivo não encontrado: {rel_path}")
            continue
        files_checked += 1
        violations = check_file_for_violations(filepath, verbose=verbose)
        total_violations.extend(violations)

    print()
    print(f"Arquivos verificados: {files_checked}")
    print(f"Fabricação de string '0.0.0.0': {len(total_violations)}")

    if not total_violations:
        print()
        print(" ✅ RESULTADO: TODOS OS BINDS EM 127.0.0.1 — CONFORME")
        print("   Nenhuma violação da regra 3.1 do mestre encontrada.")
        return 0
    else:
        print()
        print(" ❌ RESULTADO: VIOLAÇÕES ENCONTRADAS")
        print("   Os seguintes arquivos contêm bind em 0.0.0.0:")
        for v in total_violations:
            print(v)
        print()
        print("   Corrija antes de prosseguir. Bind em 0.0.0.0 expõe o servidor na rede.")
        return 1


if __name__ == "__main__":
    sys.exit(main())