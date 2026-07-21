"""Teste do Tutorial 3 — Primeiro inimigo."""
import sys; sys.path.insert(0, ".")
from server import _build_handlers

def _call(handler, args=None):
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

    for tool in ["create_entity", "physics_manage", "safety_manage"]:
        if tool not in h:
            erros.append(f"Tool {tool} nao encontrada")
        else:
            r = _call(h[tool], {"op": "status"} if tool.endswith("_manage") else {"type": "Node2D", "name": "test"})
            if "status" not in r:
                erros.append(f"Tool {tool} sem status: {r}")

    if erros:
        for e in erros: print(f"[FAIL] {e}")
        exit(1)
    print("[PASS] Tutorial 03 — todas as tools respondem")

if __name__ == "__main__": test()
