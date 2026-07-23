# ARQUITETURA_MCP.md — Arquitetura do MCP Godot Agent

**Gerado do código real.** **Data:** 2026-07-23 · **Onda:** 10.3

---

## Visão Geral

Servidor MCP em Python que é o dono do processo de desenvolvimento de um jogo Godot inteiro — da ideia ao lançamento. Expõe ~234 ferramentas curadas por fase de desenvolvimento.

## Camadas

```
┌─────────────────────────────────────────┐
│            MCP Client (IA)              │
├─────────────────────────────────────────┤
│  server.py — list_tools / call_tool     │
├─────────────────────────────────────────┤
│  core/tool_definitions.py — Tool() defs │
│  tools/rollups.py — _manage via factory │
├─────────────────────────────────────────┤
│  registry/ — fonte de verdade (futuro)  │
│  core/legacy_data.py — curadoria atual  │
├─────────────────────────────────────────┤
│  tools/ — handlers (~80 módulos)        │
│  domains/ — 38 domínios Godot           │
├─────────────────────────────────────────┤
│  Godot Engine (via bridge/addon)        │
└─────────────────────────────────────────┘
```

## Fluxo de Tool

1. `_raw_tool_defs()` → ~272 definições brutas
2. `_tool_defs()` → pós-processamento (hints, rollups, filtros)
3. Filtro toolsets (`--toolsets`) → namespaces semânticos
4. Filtro fase (`_get_phase_tools()`) → CORE + fase atual
5. Depreciação → remove 191 tools obsoletas
6. Resultado: ~234 tools visíveis

## Fases

| Fase | Tools (só fase) | Visível (+CORE 25) |
|---|---|---|
| IDEIA | 38 | 63 |
| DESIGN | 57 | 82 |
| PROTOTIPO | 14 | 39 |
| CONTEUDO | 63 | 88 |
| POLIMENTO | 42 | 67 |
| PRONTO_PARA_LANCAR | 16 | 41 |

## Namespaces (toolsets)

| Namespace | Tools |
|---|---|
| project | 71 |
| assets | 32 |
| runtime | 40 |
| analysis | 38 |
| orchestration | 55 |

## Gates

- `.githooks/pre-commit` — bloqueia commit com violação G3
- `auditar.py` — 7 critérios (C1-C7)
- `registry/invariants.py` — 11 invariantes ativas

## Meta-tools (descoberta progressiva)

`catalog_search` → `describe_tool` → `invoke_by_name` (no CORE, sempre visíveis)
