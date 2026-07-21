"""domains/_template/handlers.py — Handlers do domínio template.

Handlers são funções puras:
- Argumentos keyword-only (*)
- Não conhecem MCP, Tool, ou annotations
- Não escolhem transporte diretamente
- Retornam dict com "status"
"""


def example_handler(*, param1: str = "") -> dict:
    """Resumo de uma linha do que esta op faz."""
    return {
        "status": "success",
        "message": f"Template handler called with param1={param1}",
    }
