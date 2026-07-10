"""vscode_config.py — Auto-config MCP para VS Code / Copilot / Claude (Fase 2C).

Gera arquivos de configuração MCP automaticamente para:
- VS Code Copilot (DeepSeek V4) — ALVO PRINCIPAL
- Claude Desktop
- Cursor IDE
- Windsurf

Uso:
    python tools/vscode_config.py              # Detecta e gera tudo
    python tools/vscode_config.py --vscode     # Só VS Code
    python tools/vscode_config.py --claude     # Só Claude Desktop
    python tools/vscode_config.py --all        # Todos os clientes
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # servidor/


# ── Detecção ────────────────────────────────────────────────────────

def _get_python_cmd() -> str:
    """Retorna o comando Python (do .venv ou do sistema)."""
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _get_server_path() -> str:
    """Retorna o caminho absoluto do server.py."""
    return str(ROOT / "server.py")


def _get_server_dir() -> str:
    """Retorna o diretório do servidor."""
    return str(ROOT)


def _detect_workspaces() -> list[Path]:
    """Detecta possíveis raízes de workspace VS Code onde salvar mcp.json.
    
    Procura por:
    1. NUCLEO/ (3 níveis acima do servidor) — sempre incluso
    2. NUCLEO/projetos/*/ — subprojetos com PROMPT_INICIAL.md ou .vscode/
    3. Diretório atual se diferente dos anteriores
    """
    nucleo = ROOT.parent.parent.parent  # servidor -> mcp-godot -> sistema -> NUCLEO
    workspaces = [nucleo]
    
    projetos = nucleo / "projetos"
    if projetos.is_dir():
        for child in projetos.iterdir():
            if child.is_dir():
                # Detectar se é um projeto ativo (tem .vscode/ ou PROMPT_INICIAL.md)
                if (child / ".vscode").is_dir() or (child / "PROMPT_INICIAL.md").exists():
                    workspaces.append(child)
    
    # Também incluir cwd se diferente
    cwd = Path.cwd()
    if cwd not in workspaces:
        # Verificar se cwd parece um workspace (tem .vscode/ ou .github/)
        if (cwd / ".vscode").is_dir() or (cwd / ".github").is_dir():
            workspaces.append(cwd)
    
    return workspaces


# ── Geradores de Config ─────────────────────────────────────────────

def generate_vscode_config(output_path: str | None = None) -> dict:
    """Gera configuração para VS Code Copilot (.vscode/mcp.json).

    Args:
        output_path: Caminho para salvar (opcional). Se None, retorna só o dict.

    Returns:
        dict com a configuração gerada.
    """
    config = {
        "servers": {
            "godot-agent": {
                "type": "stdio",
                "command": _get_python_cmd(),
                "args": [_get_server_path()],
                "cwd": _get_server_dir(),
                "env": {
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONIOENCODING": "utf-8",
                },
            }
        }
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    return config


def generate_claude_config(output_path: str | None = None) -> dict:
    """Gera configuração para Claude Desktop (claude_desktop_config.json).

    Args:
        output_path: Caminho para salvar.

    Returns:
        dict com snippet para adicionar ao arquivo de config do Claude.
    """
    config = {
        "mcpServers": {
            "godot-agent": {
                "command": _get_python_cmd(),
                "args": [_get_server_path()],
                "cwd": _get_server_dir(),
            }
        }
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    return config


def generate_cursor_config(output_path: str | None = None) -> dict:
    """Gera configuração para Cursor IDE (.cursor/mcp.json)."""
    config = {
        "mcpServers": {
            "godot-agent": {
                "command": _get_python_cmd(),
                "args": [_get_server_path()],
                "cwd": _get_server_dir(),
            }
        }
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    return config


# ── Validação ───────────────────────────────────────────────────────

def validate_environment() -> dict:
    """Verifica se o ambiente está pronto para rodar o MCP.

    Returns:
        dict com status de cada componente.
    """
    results = {
        "python": {"status": "ok", "path": _get_python_cmd()},
        "server": {"status": "ok", "path": _get_server_path()},
        "venv": {"status": "ok" if (ROOT / ".venv").exists() else "warning"},
        "dependencies": {"status": "checking"},
    }

    # Verifica dependências
    try:
        import mcp  # noqa: F401
        results["dependencies"]["mcp"] = "ok"
    except ImportError:
        results["dependencies"]["mcp"] = "missing"

    try:
        import godot_parser  # noqa: F401
        results["dependencies"]["godot_parser"] = "ok"
    except ImportError:
        results["dependencies"]["godot_parser"] = "missing"

    # Verifica server.py existe
    if not (ROOT / "server.py").exists():
        results["server"]["status"] = "error"
        results["server"]["error"] = "server.py não encontrado"

    # Testa se o server importa
    try:
        subprocess.run(
            [_get_python_cmd(), "-c", "import sys; sys.path.insert(0,'.'); from server import _tool_defs; print(len(_tool_defs()))"],
            cwd=str(ROOT),
            capture_output=True,
            timeout=10,
            check=True,
        )
        results["server"]["import_test"] = "ok"
    except Exception as e:
        results["server"]["import_test"] = f"falhou: {e}"

    # Status geral
    has_errors = (
        results["server"].get("status") == "error"
        or "missing" in results.get("dependencies", {}).values()
    )
    results["overall"] = "error" if has_errors else "ok"

    return results


# ── CLI ─────────────────────────────────────────────────────────────

def auto_config(target: str = "all") -> dict:
    """Executa auto-configuração completa.

    Args:
        target: "vscode", "claude", "cursor", ou "all".

    Returns:
        dict com resultado de cada passo.
    """
    result = {"validation": validate_environment()}

    if result["validation"]["overall"] != "ok":
        result["error"] = "Ambiente não está pronto. Corrija os problemas acima."
        return result

    targets = {
        "vscode": lambda: [
            generate_vscode_config(str(ws / ".vscode" / "mcp.json"))
            for ws in _detect_workspaces()
        ],
        "claude": lambda: generate_claude_config(None),  # só imprime
        "cursor": lambda: generate_cursor_config(None),  # só imprime
    }

    if target == "all":
        for t in ["vscode", "claude", "cursor"]:
            try:
                targets[t]()
                result[t] = "ok"
            except Exception as e:
                result[t] = f"erro: {e}"
    elif target in targets:
        try:
            targets[target]()
            result[target] = "ok"
        except Exception as e:
            result[target] = f"erro: {e}"
    else:
        result["error"] = f"Alvo inválido: {target}. Use: vscode, claude, cursor, all"

    return result


# ── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-config MCP para VS Code / Copilot / Claude")
    parser.add_argument("--vscode", action="store_true", help="Configurar VS Code Copilot")
    parser.add_argument("--claude", action="store_true", help="Configurar Claude Desktop")
    parser.add_argument("--cursor", action="store_true", help="Configurar Cursor IDE")
    parser.add_argument("--all", action="store_true", help="Configurar todos")
    parser.add_argument("--validate", action="store_true", help="Apenas validar ambiente")
    parser.add_argument("--print", action="store_true", help="Imprimir config sem salvar")

    args = parser.parse_args()

    if args.validate:
        result = validate_environment()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["overall"] == "ok" else 1)

    if args.print:
        target = "vscode" if args.vscode else "claude" if args.claude else "cursor" if args.cursor else "vscode"
        if target == "vscode":
            cfg = generate_vscode_config()
            print("\n# ── VS Code Copilot (.vscode/mcp.json) ──")
            print(json.dumps(cfg, indent=2, ensure_ascii=False))
        elif target == "claude":
            cfg = generate_claude_config()
            print("\n# ── Claude Desktop ──")
            print(json.dumps(cfg, indent=2, ensure_ascii=False))
        sys.exit(0)

    target = "vscode" if args.vscode else "claude" if args.claude else "cursor" if args.cursor else "all"
    result = auto_config(target)
    print(json.dumps(result, indent=2, ensure_ascii=False))
