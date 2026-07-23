# ONDA P — PENDENCIAS

> Tudo que ficou solto. Uma fatia por item.

## Fatia P.1 — Feature 9: trava de exportacao
1. O que e: build_export <- release_checklist. Fase 1 do MCP, nunca iniciada.
8. Como provar: python auditar.py --fatia P.1
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia P.2 — Feature 10: proximo passo obrigatorio
1. O que e: get_next_step obrigatorio no inicio da sessao.
8. Como provar: python -m pytest tests/test_feature10.py -v
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia P.3 — set_node_property/get_node_property
1. O que e: set_node_property grava mas get_node_property devolve null.
8. Como provar: python -m pytest tests/test_node_property.py -v
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.4 — INV-03: execute_gdscript_runtime
1. O que e: Teste falhando alegado falso positivo sem prova.
8. Como provar: python -m pytest tests/ -k INV-03 -v
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.5 — 362 testes vs 166 reportados
1. O que e: Divergencia entre coleta e reporte.
8. Como provar: python -m pytest --collect-only -q | Measure-Object -Line
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.6 — AGENTS.md secao 2 quebrada
1. O que e: Bloco de codigo fecha sem abrir.
8. Como provar: findstr /N "''" AGENTS.md
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.7 — config.local.json ausente
1. O que e: Criar config.local.json.example.
8. Como provar: Test-Path config.local.json.example
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.8 — Consistencia dos 38 dominios
1. O que e: Auditoria de integridade dos dominios (6 arquivos cada).
8. Como provar: python -c "from pathlib import Path; [print(d.name, len(list(Path('domains',d.name).glob('*.py')))) for d in Path('domains').iterdir() if d.is_dir()]"
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.9 — .mcp_proof nunca exercitado
1. O que e: Sistema de provas nunca usado; transicoes 80% forcadas.
8. Como provar: Get-ChildItem -Recurse -Filter .mcp_proof
10. Marcacao: [SENIOR] [EIXO-CENTRAL]

## Fatia P.10 — 22 mencoes a cline
1. O que e: Residuos em instalar.py e instalar_roadmap.py.
8. Como provar: findstr /S /N /C:"cline" instalar.py instalar_roadmap.py
10. Marcacao: [AUTO] [EIXO-CENTRAL]

## Fatia P.11 — ruff no venv
1. O que e: Instalar ruff para linter.
8. Como provar: .venv/Scripts/python -m ruff --version
10. Marcacao: [AUTO] [EIXO-CENTRAL]
