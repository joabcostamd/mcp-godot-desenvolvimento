"""Teste do Tutorial 1 — Primeiro projeto.

Simula chamadas reais das tools na ordem do tutorial.
"""
import sys; sys.path.insert(0, ".")
from server import _build_handlers

def _call(handler, args=None):
    """Chama handler com args dict ou vazio, tratando assinatura."""
    try:
        return handler(**(args or {}))
    except TypeError:
        try:
            return handler(args or {})
        except TypeError:
            return handler()

def test():
    h = _build_handlers()
    erros = []

    # Passo 1: ping e health_check
    for tool in ["ping", "health_check"]:
        if tool not in h:
            erros.append(f"Tool {tool} nao encontrada")
        else:
            r = _call(h[tool])
            if r.get("status") != "success":
                erros.append(f"Tool {tool} falhou: {r}")

    # Passo 2: get_next_step
    if "get_next_step" not in h:
        erros.append("Tool get_next_step nao encontrada")
    else:
        r = _call(h["get_next_step"])
        if "status" not in r:
            erros.append(f"get_next_step sem status: {r}")

    # Passo 3: set_project_brief
    if "set_project_brief" not in h:
        erros.append("Tool set_project_brief nao encontrada")
    else:
        r = _call(h["set_project_brief"], {"description": "Jogo de plataforma 2D"})
        if "status" not in r:
            erros.append(f"set_project_brief sem status: {r}")

    # Passo 5: get_current_phase
    if "get_current_phase" not in h:
        erros.append("Tool get_current_phase nao encontrada")
    else:
        r = _call(h["get_current_phase"])
        if "status" not in r:
            erros.append(f"get_current_phase sem status: {r}")

    if erros:
        for e in erros: print(f"[FAIL] {e}")
        exit(1)
    print("[PASS] Tutorial 01 — todas as tools respondem")

if __name__ == "__main__": test()
