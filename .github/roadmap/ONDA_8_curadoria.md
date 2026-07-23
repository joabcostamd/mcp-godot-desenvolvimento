# ONDA 8 — CURADORIA

> 59 tools sem fase.

## Fatia 8.1 — Atribuir fase a toda tool

1. O que e: Toda tool em >=1 fase ou internal=True. INV-04.
8. Como provar: python -c "from server import _tool_defs; [print(t.name) for t in _tool_defs() if not hasattr(t,'phase')]"
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia 8.2 — Reduzir filtros de 3 para 2 eixos

1. O que e: Consolidar profile/toolsets/phase em 2 eixos.
8. Como provar: python auditar.py --fatia 8.2
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia 8.3 — Documentar precedencia atual

1. O que e: Documentar ordem de precedencia dos filtros antes de mudar.
8. Como provar: Test-Path docs/CURADORIA_PRECEDENCIA.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]
