#!/usr/bin/env python3
"""audit_descriptions.py — Auditoria de descricoes de tools (FATIA 2.AO).

Verifica todas as tools registradas contra criterios de qualidade:
- Tamanho maximo de descricao (token budget)
- Distinguibilidade entre tools (Levenshtein)
- Presenca de palavras-chave obrigatorias
- Descricao inchada (mais de 300 chars)

Uso:
    python scripts/audit_descriptions.py              # relatorio completo
    python scripts/audit_descriptions.py --max-len 200  # limite customizado
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calcula similaridade entre duas strings (0.0 = totalmente diferente, 1.0 = identica)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    # Matriz de distancia
    dist = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dist[i][0] = i
    for j in range(len2 + 1):
        dist[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dist[i][j] = min(
                dist[i - 1][j] + 1,       # delecao
                dist[i][j - 1] + 1,       # insercao
                dist[i - 1][j - 1] + cost  # substituicao
            )

    max_len = max(len1, len2)
    return 1.0 - (dist[len1][len2] / max_len)


def audit_descriptions(max_len: int = 250) -> dict:
    """Audita todas as descricoes de tools.

    Returns:
        dict com relatorio completo.
    """
    from core.tool_definitions import _raw_tool_defs

    tools = _raw_tool_defs()

    report = {
        "total_tools": len(tools),
        "max_length_limit": max_len,
        "issues": {
            "too_long": [],
            "too_similar": [],
            "too_short": [],
            "missing_keywords": [],
        },
        "stats": {
            "avg_length": 0,
            "max_length": 0,
            "min_length": 999,
            "longest_tool": "",
            "shortest_tool": "",
        },
    }

    total_len = 0
    for tool in tools:
        desc = tool.description
        name = tool.name
        length = len(desc)

        total_len += length
        if length > report["stats"]["max_length"]:
            report["stats"]["max_length"] = length
            report["stats"]["longest_tool"] = name
        if length < report["stats"]["min_length"]:
            report["stats"]["min_length"] = length
            report["stats"]["shortest_tool"] = name

        # Check: too long
        if length > max_len:
            report["issues"]["too_long"].append({
                "name": name,
                "length": length,
                "excerpt": desc[:80] + "...",
            })

        # Check: too short (menos de 30 chars = provavelmente pouco informativa)
        if length < 30:
            report["issues"]["too_short"].append({
                "name": name,
                "length": length,
                "description": desc,
            })

        # Check: missing keywords
        has_pt = any(kw in desc.lower() for kw in ["use", "cria", "gera", "lista", "verifica", "analisa", "aplica"])
        has_en = any(kw in desc.lower() for kw in ["use", "create", "generate", "list", "verify", "analyze", "apply"])
        if not has_pt and not has_en:
            report["issues"]["missing_keywords"].append({
                "name": name,
                "description": desc[:100],
            })

    # Check: too similar (pares com similaridade > 85%)
    for i in range(len(tools)):
        for j in range(i + 1, len(tools)):
            ratio = levenshtein_ratio(tools[i].description, tools[j].description)
            if ratio > 0.85:
                report["issues"]["too_similar"].append({
                    "tool_a": tools[i].name,
                    "tool_b": tools[j].name,
                    "similarity": f"{ratio:.1%}",
                })

    report["stats"]["avg_length"] = total_len // len(tools) if tools else 0

    # Score
    total_issues = sum(len(v) for v in report["issues"].values())
    report["score"] = "A" if total_issues == 0 else (
        "B" if total_issues <= 5 else (
            "C" if total_issues <= 15 else "D"
        )
    )

    return report


def main():
    parser = argparse.ArgumentParser(description="Audita descricoes de tools MCP")
    parser.add_argument("--max-len", type=int, default=250, help="Tamanho maximo aceitavel (default: 250)")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    args = parser.parse_args()

    report = audit_descriptions(max_len=args.max_len)

    if args.json:
        import json
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== AUDITORIA DE DESCRICOES (limite: {args.max_len} chars) ===")
        print(f"Total tools: {report['total_tools']}")
        print(f"Media: {report['stats']['avg_length']} chars")
        print(f"Mais longa: {report['stats']['longest_tool']} ({report['stats']['max_length']} chars)")
        print(f"Mais curta: {report['stats']['shortest_tool']} ({report['stats']['min_length']} chars)")
        print(f"\n--- PROBLEMAS ---")
        print(f"Muito longas (> {args.max_len}): {len(report['issues']['too_long'])}")
        for item in report['issues']['too_long'][:5]:
            print(f"  {item['name']}: {item['length']} chars — {item['excerpt']}")
        print(f"Muito similares (> 85%): {len(report['issues']['too_similar'])}")
        for item in report['issues']['too_similar'][:5]:
            print(f"  {item['tool_a']} <-> {item['tool_b']}: {item['similarity']}")
        print(f"Muito curtas (< 30): {len(report['issues']['too_short'])}")
        print(f"Sem verbo de acao: {len(report['issues']['missing_keywords'])}")
        print(f"\nScore: {report['score']}")

        total_issues = sum(len(v) for v in report['issues'].values())
        if total_issues == 0:
            print("\n[PASS] Todas as descricoes dentro do padrao lean.")
        else:
            print(f"\n[FAIL] {total_issues} problema(s) encontrado(s).")

    sys.exit(0 if report['score'] in ('A', 'B') else 1)


if __name__ == "__main__":
    main()
