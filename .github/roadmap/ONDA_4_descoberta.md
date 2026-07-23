# ONDA 4 — DESCOBERTA PROGRESSIVA

> Derivada de docs/REORG_ROADMAP.md §4. 4.1 ja feito (trio em PHASE_TOOLS_CORE).

## Fatia 4.2 — Fundir tool_catalog/tool_groups em catalog_search

1. O que e: Unificar 3 tools de descoberta em 1.
2. Por que agora: Trio ja existe, so esta orfao.
8. Como provar: python -c "from server import _tool_defs; ns=[t.name for t in _tool_defs() if 'catalog' in t.name or 'tool_group' in t.name]; print(ns)"
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 4.3 — Indexar ops, nao so tools

1. O que e: catalog_search devolve ops dentro de rollups.
8. Como provar: python -c "from tools.rollups import _ROLLUP_BUILDERS; print(len(_ROLLUP_BUILDERS))"
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 4.4 — describe_tool({tool, op})

1. O que e: describe_tool aceita parametro op para detalhar operacao dentro de rollup.
8. Como provar: python -m pytest tests/test_descoberta.py -v -k describe
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia 4.5 — Guia no AGENTS.md

1. O que e: Documentar uso do trio de descoberta no fluxo de trabalho.
8. Como provar: findstr /N "catalog_search" AGENTS.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]
