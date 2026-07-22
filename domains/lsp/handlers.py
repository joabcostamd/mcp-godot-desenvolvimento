"""domains/lsp/handlers.py — Handlers do domínio lsp (F5.10).

Wrappers keyword-only (*) que delegam para tools/lsp_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def gdscript_lsp_connect(*, project_root: str | None = None) -> dict:
    """Conecta ao Language Server do Godot na porta 6005."""
    from tools.lsp_ops import gdscript_lsp_connect as _impl
    return _impl(project_root=project_root)


def gdscript_lsp_disconnect() -> dict:
    """Desconecta do Language Server do Godot."""
    from tools.lsp_ops import gdscript_lsp_disconnect as _impl
    return _impl()


def gdscript_sync_file(*, file_path: str, content: str | None = None) -> dict:
    """Notifica o LSP sobre alterações em um arquivo GDScript."""
    from tools.lsp_ops import gdscript_sync_file as _impl
    return _impl(file_path=file_path, content=content)


def gdscript_definition(*, file_path: str, line: int, character: int) -> dict:
    """Navega para a definição de um símbolo GDScript."""
    from tools.lsp_ops import gdscript_definition as _impl
    return _impl(file_path=file_path, line=line, character=character)


def gdscript_references(*, file_path: str, line: int, character: int) -> dict:
    """Encontra todas as referências a um símbolo no código GDScript."""
    from tools.lsp_ops import gdscript_references as _impl
    return _impl(file_path=file_path, line=line, character=character)


def gdscript_hover(*, file_path: str, line: int, character: int) -> dict:
    """Exibe tipo e documentação de um símbolo GDScript."""
    from tools.lsp_ops import gdscript_hover as _impl
    return _impl(file_path=file_path, line=line, character=character)


def gdscript_symbols(*, file_path: str) -> dict:
    """Lista todos os símbolos (funções, classes, variáveis) de um arquivo."""
    from tools.lsp_ops import gdscript_symbols as _impl
    return _impl(file_path=file_path)


def gdscript_rename(*, file_path: str, line: int, character: int, new_name: str) -> dict:
    """Renomeia um símbolo GDScript em todo o projeto com segurança semântica."""
    from tools.lsp_ops import gdscript_rename as _impl
    return _impl(file_path=file_path, line=line, character=character, new_name=new_name)


def gdscript_diagnostics(*, file_path: str) -> dict:
    """Retorna erros e warnings do compilador GDScript para um arquivo."""
    from tools.lsp_ops import gdscript_diagnostics as _impl
    return _impl(file_path=file_path)


__all__ = [
    "gdscript_lsp_connect",
    "gdscript_lsp_disconnect",
    "gdscript_sync_file",
    "gdscript_definition",
    "gdscript_references",
    "gdscript_hover",
    "gdscript_symbols",
    "gdscript_rename",
    "gdscript_diagnostics",
]
