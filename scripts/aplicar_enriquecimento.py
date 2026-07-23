#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Aplica as propostas de enriquecimento aos behavior.json.

Uso: python scripts/aplicar_enriquecimento.py [--lote N] [--todos]

Sem --lote: aplica o lote 1 (behaviors #1-25).
Com --lote N: aplica o lote N (behaviors #(N-1)*25+1 a N*25).
Com --todos: aplica todos os 249 de uma vez.
"""

import json
import os
import sys

BEHAVIORS_ROOT = os.path.join(os.path.dirname(__file__), "..", "behaviors")
PROPOSTAS_FILE = os.path.join(BEHAVIORS_ROOT, "_enriquecimento_proposto.json")


def load_propostas():
    with open(PROPOSTAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_behavior_names_sorted():
    return sorted([d for d in os.listdir(BEHAVIORS_ROOT)
                   if os.path.isdir(os.path.join(BEHAVIORS_ROOT, d))
                   and os.path.isfile(os.path.join(BEHAVIORS_ROOT, d, "behavior.json"))])


def apply_batch(behavior_names, propostas, dry_run=False):
    """Aplica os 4 campos novos nos behavior.json."""
    applied = []
    skipped = []
    errors = []

    for name in behavior_names:
        if name not in propostas:
            skipped.append(name)
            continue

        bjson_path = os.path.join(BEHAVIORS_ROOT, name, "behavior.json")
        try:
            with open(bjson_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            errors.append((name, str(e)))
            continue

        p = propostas[name]

        # Verifica se já tem os campos (não sobrescrever sem querer)
        already_has = all(k in data for k in ["combina_bem", "custo", "verbo_pt", "verbo_en", "nivel"])
        if already_has:
            # Atualiza mesmo assim (pode ser re-execução com valores melhores)
            pass

        data["combina_bem"] = p["combina_bem"]
        data["custo"] = p["custo"]
        data["verbo_pt"] = p["verbo_pt"]
        data["verbo_en"] = p["verbo_en"]
        data["nivel"] = p["nivel"]

        if not dry_run:
            with open(bjson_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")

        applied.append(name)

    return applied, skipped, errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aplica enriquecimento aos behavior.json")
    parser.add_argument("--lote", type=int, default=1, help="Número do lote (1-10)")
    parser.add_argument("--todos", action="store_true", help="Aplicar todos os 249")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simular, sem escrever")
    args = parser.parse_args()

    propostas = load_propostas()
    all_names = get_behavior_names_sorted()

    if args.todos:
        batch = all_names
        label = "TODOS"
    else:
        lote_size = 25
        start = (args.lote - 1) * lote_size
        end = min(start + lote_size, len(all_names))
        batch = all_names[start:end]
        label = "Lote %d" % args.lote

    print("=" * 60)
    print("APLICAR ENRIQUECIMENTO - %s" % label)
    print("=" * 60)
    print("Behaviors no lote: %d" % len(batch))
    print("Dry run: %s" % args.dry_run)
    print()

    if args.dry_run:
        print("--- Simulacao (dry-run) ---")
        for name in batch:
            p = propostas.get(name, {})
            print("  %s: custo=%s, nivel=%s, verbo_pt=%s, cb=%d itens" % (
                name, p.get("custo", "?"), p.get("nivel", "?"),
                p.get("verbo_pt", "?"), len(p.get("combina_bem", []))))
        print("\n[DRY-RUN] Nenhum arquivo foi alterado.")
        return

    applied, skipped, errors = apply_batch(batch, propostas)

    print("Aplicados: %d" % len(applied))
    if skipped:
        print("Pulado (sem proposta): %d" % len(skipped))
        for s in skipped:
            print("  - %s" % s)
    if errors:
        print("Erros: %d" % len(errors))
        for name, err in errors:
            print("  - %s: %s" % (name, err))

    print("\nBehaviors alterados:")
    for name in applied:
        p = propostas[name]
        print("  %s: custo=%s, nivel=%s, verbo_pt=%s, verbo_en=%s, cb=%d" % (
            name, p["custo"], p["nivel"], p["verbo_pt"], p["verbo_en"],
            len(p["combina_bem"])))

    print("\nPronto.")


if __name__ == "__main__":
    main()
