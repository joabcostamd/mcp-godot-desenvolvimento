"""Teste do Tutorial 2 — Primeira cena.

Simula chamadas reais das tools na ordem do tutorial.
"""
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

    # Passo 1: scene_manage (criar cena)
    if "scene_manage" not in h:
        erros.append("Tool scene_manage nao encontrada")
    else:
        r = _call(h["scene_manage"], {"op": "create", "name": "main"})
        if "status" not in r:
            erros.append(f"scene_manage sem status: {r}")

    # Passo 2: create_entity (personagem)
    if "create_entity" not in h:
        erros.append("Tool create_entity nao encontrada")
    else:
        r = _call(h["create_entity"], {"type": "CharacterBody2D", "name": "Player"})
        if "status" not in r:
            erros.append(f"create_entity sem status: {r}")

    # Passo 4: node_manage (ajustar propriedades)
    if "node_manage" not in h:
        erros.append("Tool node_manage nao encontrada")
    else:
        r = _call(h["node_manage"], {"op": "set_property", "node_path": "Player", "property": "scale"})
        if "status" not in r:
            erros.append(f"node_manage sem status: {r}")

    if erros:
        for e in erros: print(f"[FAIL] {e}")
        exit(1)
    print("[PASS] Tutorial 02 — todas as tools respondem")

if __name__ == "__main__": test()
