# CONTEXTO_PROJETO_MCP_GODOT — Status em 2026-07-18

## Roadmap Camada 0 — Andamento

### Concluídas (19 fatias)

| Fatia | Status | Resultado |
|---|---|---|
| 0.0 — Bootstrap | ✅ | `.clinerules/` criado, workflows `/plan` `/act`, commit `1064ce4` |
| 0.0.1 — Verificação Ambiente | ✅ | 6/6 diagnósticos OK, MCP desconectado |
| 0.0.5 — `auditar.py` | ✅ | Portão executável, 6 critérios, fail-closed |
| 0.14 — Governador | ✅ | `tools/governor.py` 325 linhas, 7/7 testes |
| Rebalanceamento | ✅ | 0.4: [SÊNIOR]→[AUTO] |
| 0.1 — Inventário | ✅ | `INVENTARIO_OPS_ROLLUPS.md`, 28 rollups, 115 ops |
| 0.2 — Impacto MCP spec | ✅ | 0 referências a `-32002` |
| 0.3 — Comportamento Cline | ✅ | Roo Code 3.54, `/plan` `/act` funcionam |
| 0.4 — Bind loopback | ✅ | `verify_loopback.py`: 0 violações |
| 0.5 — Git segurança | ✅ | `_auto_checkpoint()` em `safety.py` |
| 0.6 — Gestão segredo | ✅ | `scan_secrets()`: 0 segredos |
| 0.8 — Gate CI | ✅ | `tests/test_budget_gate.py` funcional |
| 0.10 — Migração schema | ✅ | `tools/schema_migration.py` existe |
| 0.11 — Contract snapshot | ✅ | `tests/contract_snapshot.py` 296 linhas |
| 0.12 — Kill switch | ✅ | `tools/kill_switch.py` existe |
| 0.13 — Idempotência | ✅ | `tools/idempotency_audit.py` existe |
| 0.15 — Perfil lean | ✅ | Meta-tools no core + handlers |
| 0.7a — Consolidar game_* | ✅ | 14 `game_*` → `game_bridge_manage`. PROTOTIPO: 92→79 |
| 0.9 — Cliente HTTP | ✅ | `tools/external_client.py` 233 linhas, rate-limit+retry+idempotência |

### Bloqueadas (1)

| Fatia | Motivo |
|---|---|
| 0.7b — Consolidar godot_* | 7/9 funções são handlers inline no `server.py`, não importáveis. Requer refatoração prévia |

### Pendentes (3)

| Fatia | O que falta |
|---|---|
| 0.16 — Medição tokens | Estender `test_budget_gate.py` para somar tokens de definição |
| 0.7b+ — Consolidação restante | Extrair funções inline do `server.py`, depois consolidar em rollups |
| C5 — Teto >40 | 6 fases >40 tools visíveis (pré-existente). Fatia 0.7 responsável |

### Git log (últimos commits)

```
cdd29f3 feat: external_client.py — cliente HTTP compartilhado (Fatia 0.9)
9526c78 feat: game_bridge_manage rollup — consolida 14 game_* tools (Fatia 0.7a)
4e522fd fix: remover emojis do auditar.py (compatibilidade Windows cp1252)
2d83db6 docs: rebalanceamento de marcacoes (0.4: SENIOR->AUTO)
6acc1cb feat: auditar.py + testes do governador (Fatias 0.0.5 e 0.14)
1064ce4 chore: bootstrap roadmap Memory Bank
```

### Próximo passo

**Fatia 0.16 — Medição de tokens [AUTO]:** estender `test_budget_gate.py` para somar tokens das definições de tool (nome + descrição + inputSchema).  

---

## Arquivos criados nesta sessão

| Arquivo | Descrição |
|---|---|
| `auditar.py` | Portão executável de autoauditoria (6 critérios C1-C6) |
| `tests/test_governor.py` | 7 testes de confirmação do governador |
| `tools/external_client.py` | Cliente HTTP compartilhado (rate-limit, retry, idempotência) |
| `.roadmap_progress.json` | Registro de progresso do roadmap |

---

## Opção C: aprovada ✅

**CORE sempre visível + tools da fase atual (não-cumulativo).**

- **Código:** `server.py` — `PHASE_TOOLS_CORE` (27 tools) + `_get_phase_tools()` reescrita
- **Perfil padrão:** `full`
- **Filtro:** `CORE ∪ PHASE_TOOLSETS[phase]`

### Contagem por fase

| Fase | Core | Exclusivas | Total |
|---|------|-----------|-------|
| IDEIA | 27 | 36 | 45 |
| DESIGN | 27 | 30 | 48 |
| PROTOTIPO | 27 | 52 | 79 |
| CONTEUDO | 27 | 35 | 62 |
| POLIMENTO | 27 | 30 | 57 |
| PRONTO_PARA_LANCAR | 27 | 18 | 45 |
| Total (tools de topo) | — | — | 45 |

---

## Pendências registradas

1. **C5 — Teto de tools:** 6 fases >40 tools visíveis. Origem: pré-existente (commit `f056aed8`, 12/07/2026). Fatia responsável: 0.7 (consolidação). Bloqueada por 0.7b (funções `godot_*` são inline).
2. **0.7b — Consolidação PROTOTIPO:** 9 `godot_*` não são importáveis. Requer extração de handlers inline do `server.py` para módulo separado.
3. **Cross-model:** Nunca feito em modo FORTE. Todas as verificações foram "fraca" (mesma janela).
4. **Branches safety** `safety/fatia-0.7`, `safety/fatia-0.7b`, `safety/fatia-0.1`, `safety/fatia-0.14`, `safety/fatia-rebalanceamento` — podem ser removidas.

---

**Sessão 18/07/2026 — Camada 0 ~80% concluída.**