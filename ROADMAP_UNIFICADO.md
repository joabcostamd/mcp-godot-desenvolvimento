# 🗺️ ROADMAP UNIFICADO — MCP Godot Agent v3.4+

> **Versão:** 3.0.0 | **Criado em:** 2026-07-19 | **Atualizado:** 2026-07-19 (automação)
>
> **Objetivo:** Coordenar 2 IAs agenticas (ambas GitHub Copilot) em um pipeline
> **totalmente autônomo** de desenvolvimento, sem conflitos, usando estratégia
> "Meet in the Middle" com Zona de Sutura congelada.
>
> **Agentes ativos:**
> - 🅰️ **AGENTE 01** — Copilot DeepSeek V4 Pro — Foco: Arquitetura & Core
> - 🅱️ **AGENTE 02** — Copilot (outra instância) — Foco: Extensões & Qualidade
>
> **Este documento é AUTO-EXECUTÁVEL.** Uma vez salvo na raiz do projeto, os
> agentes seguem o fluxo automaticamente ao encontrar os arquivos de instrução
> complementares (`.github/copilot-instructions.md`, agentes, prompts, hooks).
>
> **Documentos que este plano substitui (já deletados):**
> `pendenciasMCP.md`, `NEXT_SESSION.md`, `SESSION_NEXT.md`, `MCP_ESTADO_ATUAL.md`,
> `pendencias.md`, `SESSION_SUMMARY_2026-07-17.md`, `RELOGIO_CLINE_COMPORTAMENTO.md`

---

## 🤖 SISTEMA DE AUTOMAÇÃO AGENTICA (AUTO-PIPELINE)

> **Este é o coração do sistema autônomo. Leia ANTES de qualquer outra seção.**

### Visão Geral do Ciclo Autônomo

```
┌─────────────────────────────────────────────────────────────────────┐
│                  🔄 CICLO AUTÔNOMO CONTÍNUO                           │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │PLANEJAR  │───▶│IMPLEMENTAR│───▶│ AUDITAR  │───▶│PLANEJAR  │       │
│  │próxima   │    │a etapa   │    │o que foi │    │próxima   │──╮    │
│  │etapa     │    │atual     │    │feito     │    │etapa     │  │    │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │    │
│       ▲                                                         │    │
│       └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  GATES AUTOMÁTICOS (Hooks + Auditoria):                              │
│  ├─ PreToolUse: Bloquear comandos destrutivos                        │
│  ├─ PostToolUse: Rodar validação após cada tool                      │
│  └─ Stop: Gerar HANDOFF.md + atualizar ROADMAP                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Como o Sistema Funciona na Prática

#### Passo 1 — O Humano Inicia (1x por etapa)

O Joab abre o VS Code e digita NO chat do Copilot:

```
/seguir-roadmap
```

Isso dispara o prompt file que inicia o ciclo.

#### Passo 2 — O Agente Lê o Contexto (automático)

O agente ativo (AGENTE 01 ou AGENTE 02) automaticamente:
1. Lê `ROADMAP_UNIFICADO.md` → identifica a PRÓXIMA etapa pendente da sua zona
2. Lê `SUTURE_ISSUES.md` → verifica conflitos
3. Lê `HANDOFF.md` → vê o que o outro agente fez desde a última sessão

#### Passo 3 — Planejar (via /plan interno)

O agente executa um mini-planejamento da etapa:
- Pesquisa os arquivos que vai modificar
- Confirma que não pisa nos arquivos do outro agente (matriz de conflito)
- Gera o plano interno

#### Passo 4 — Implementar (Agent Mode)

O agente implementa EXATAMENTE 1 etapa:
- Edita apenas seus arquivos exclusivos
- Segue os gates definidos nos hooks
- Roda validação após cada mudança

#### Passo 5 — Auditar (via auditor automático)

Hook `Stop` dispara automaticamente:
1. `validate_tool_registry_consistency()` — se AGENTE 01
2. `auditar.py` C1-C6 — se AGENTE 02
3. Se FAIL → o agente corrige ANTES de finalizar

#### Passo 6 — Handoff + Planejar Próxima (automático)

Ao finalizar:
1. Atualiza `ROADMAP_UNIFICADO.md` (marca etapa como ✅)
2. Escreve `HANDOFF.md` (o que fez, o que NÃO fez, alertas)
3. Atualiza `NEXT_STEP.md` (qual a próxima etapa de cada agente)
4. Faz commit com mensagem padronizada

---

### Arquivos que Materializam a Automação

> **IMPORTANTE:** Estes arquivos DEVEM ser criados junto com este documento.
> Sem eles, a automação NÃO funciona — os agentes operam no modo manual tradicional.

| Arquivo | Função | Status |
|---|---|---|
| `ROADMAP_UNIFICADO.md` | Fonte única da verdade + pipeline | ✅ v3.0 |
| `.github/copilot-instructions.md` | Regras always-on para ambos agentes | ✅ |
| `.github/prompts/seguir-roadmap.prompt.md` | Comando `/seguir-roadmap` | ✅ |
| `.github/agents/agente-01-core.agent.md` | Agente especializado AGENTE 01 | ✅ |
| `.github/agents/agente-02-extensoes.agent.md` | Agente especializado AGENTE 02 | ✅ |
| `.github/hooks/post-tool-use.json` | Hook de validação automática | ✅ |
| `NEXT_STEP.md` | Gatilho de próxima etapa | ✅ |
| `SUTURE_ISSUES.md` | Canal de conflitos | ✅ |
| `HANDOFF.md` | Comunicação entre agentes | ✅ |
| `DATA_CONTRACTS.md` | Contratos formais (Etapa A3) | 📋 Futuro |
| `INVENTARIO_OPS_ROLLUPS.md` | Catálogo de rollups | ✅ Ativo |
| `.roadmap_progress.json` | Progresso das fatias | ✅ Ativo |
| `AUDIT_PROTOCOL.md` | Protocolo C1-C6 | ✅ Ativo |

---

## 🔒 ZONA DE SUTURA — Contratos Congelados

> **Regra de Ouro:** NENHUM agente edita estes arquivos. Mudanças só acontecem
> entre etapas, com aprovação do Joab, registradas em `SUTURE_ISSUES.md`.

| Arquivo | Motivo | Última modificação |
|---|---|---|
| `tools/deprecated.py` | Set unificado — ambos dependem | Etapa A0 ✅ |
| `ROADMAP_UNIFICADO.md` | Fonte única da verdade | Esta sessão |
| `SUTURE_ISSUES.md` | Canal de conflitos | ✅ Criado |
| `DATA_CONTRACTS.md` | Interface formal Tool/Handler | Etapa A3 |

---

## 🅰️ AGENTE 01 — Da Arquitetura para as Features

> **Direção:** Do núcleo → para fora | **Arquivos:** `server.py`, `core/*`, `tools/deprecated.py`, `tools/registry_validation.py`, `tools/rollups.py`

### ✅ A0 — Limpeza Imediata (Sprint 0.5)

| Ação | Status |
|---|---|
| 3 bridges → `backups/` | ✅ |
| `_DEPRECATED` + `_DEPRECATED_H` → `tools/deprecated.py` | ✅ |
| 55 funções com `# INTERNAL: usado por <rollup>` | ✅ |
| Imports residuais limpos em `server.py` | ✅ |
| `validate_tool_registry_consistency()` → 0 `tools_sem_handler` | ✅ |

### ✅ A1 — 5 Namespaces Semânticos (~1.5h) — CONCLUÍDO 2026-07-19

**Meta:** Reduzir ~60 tools visíveis → ≤20. Resolver C5 (teto de tools).
**NÃO MEXER:** `tools/deprecated.py`, rollups, handlers

| # | Ação | Arquivo | Status |
|---|---|---|---|
| A1.1 | Criar namespaces: PROJECT, ASSETS, RUNTIME, ANALYSIS, ORCHESTRATION | `server.py` (TOOLSETS) | ✅ |
| A1.2 | Adicionar campo `namespace` em cada `Tool()` | `server.py` (_tool_defs) | ✅ |
| A1.3 | Criar `tool_groups` hierárquico (namespace → tools) | `server.py`, `tools/dynamic_groups.py` | ✅ |
| A1.4 | Testar `--profile dev` — zero perda | — | ✅ |

**Gate:** `tool_groups` mostra 5 namespaces. Zero tools perdidas. C5 reduzido. ✅

### ✅ A2 — ExecutionContext (~2h) — CONCLUÍDO 2026-07-19

**Meta:** IA nunca mais digitar `scene_path`. Contexto injetado automaticamente.

| # | Ação | Arquivo | Status |
|---|---|---|---|
| A2.1 | Criar `ExecutionContext` dataclass | `core/context.py` (novo) | ✅ |
| A2.2 | Implementar `_dispatch_with_context` que carrega contexto antes de cada tool | `server.py` (call_tool) | ✅ |
| A2.3 | Cache de `scene_tree` com TTL 5s | `core/context.py` | ✅ |
| A2.4 | Tools de cena → `scene_path` implícito (via contexto) | `tools/scene_ops.py` | ✅ |

**Gate:** `scene_manage(op="create")` funciona SEM parâmetro `scene_path`. ✅
- `_resolve_scene_path_from_vibe()` agora consulta `ExecutionContext.active_scene`
- `paint_tilemap_cell` e `detect_offscreen_elements` ganharam fallback
- Contexto injetado via thread-local em `_dispatch_with_context`

### ⬜ A3 — DATA_CONTRACTS.md (~1h)

**Meta:** Criar o contrato formal entre os agentes. ZERO código.

| # | Ação | Arquivo |
|---|---|---|
| A3.1 | Documentar `Tool(name, description, inputSchema)` | `DATA_CONTRACTS.md` |
| A3.2 | Documentar interface `ToolRegistry` | `DATA_CONTRACTS.md` |
| A3.3 | Documentar pipeline `_tool_defs → handlers → call_tool` | `DATA_CONTRACTS.md` |

**Gate:** `DATA_CONTRACTS.md` existe. Ambos os agentes podem consultar.

### ⬜ A4 — Intent Router (~4h)

**Meta:** `godot(action="criar inimigo")` — 1 chamada resolve tudo.

| # | Ação | Arquivo |
|---|---|---|
| A4.1 | ~100 regex PT+EN | `core/intent_router.py` (novo) |
| A4.2 | Pipeline: `classify → route → extract → invoke` | `core/intent_router.py` |
| A4.3 | Handler `godot()` | `server.py` |
| A4.4 | Fallback `tool_catalog` | `server.py` |
| A4.5 | Testar 20 intenções variadas | — |

**Gate:** `godot(action="criar inimigo com patrulha")` funciona. ≥95% cobertura.

### ⬜ A5 — Refatorações Estruturais (~4h)

**Meta:** `server.py` ≤ 3500 linhas. Código modular e testável.
⚠️ Risco moderado com Etapas B5/B7/B8 do AGENTE 02

| # | Ação | Arquivo |
|---|---|---|
| A5.1 | Extrair `ToolRegistry` (~2800 linhas) | `core/tool_registry.py` (novo) |
| A5.2 | Extrair `MCPConnectionManager` | `core/connection_manager.py` (novo) |
| A5.3 | Migrar `server.py` → imports das novas classes | `server.py` |
| A5.4 | `validate_tool_registry_consistency()` — zero regressão | — |

**Gate:** `wc -l server.py` ≤ 3500. `--profile dev` idêntico ao pré-refatoração.

### ⬜ A6 — Qualidade MCP Spec (~3h)

**Meta:** Conformidade 12/14 com spec MCP 2025-11-25.

| # | Ação | Arquivo |
|---|---|---|
| A6.1 | `validate_environment()` no boot | `server.py` |
| A6.2 | Health check expansivo | `server.py` |
| A6.3 | Logs estruturados JSON | `server.py` |
| A6.4 | `isError`, `structuredContent`, `outputSchema` | `server.py` |
| A6.5 | Tool `annotations` (audience, priority, lastModified) | `server.py` |

**Gate:** Conformidade MCP Spec 12/14.

---

## 🅱️ AGENTE 02 — Das Extensões para o Core

> **Direção:** Das ferramentas → para dentro | **Arquivos:** `tools/*_ops.py`, `.github/workflows/`, `docs/`, `tests/`
> **Status:** 55/96 fatias concluídas (Camadas 0-3 ✅, Camada 4: 1/9)

### ✅ CONCLUÍDO

| Camada | Progresso |
|---|---|
| 0 — Fundação e Segurança | ✅ 16/16 |
| 1 — Experiência do Dev | ✅ 16/16 |
| 2 — Testes | ✅ 7/7 (2.5 escalada) |
| 3 — Criação com Fosso | ✅ 16/16 (3.1-3.4 escaladas) |
| B1 (4.1) — i18n testing | ✅ |
| B2 (4.2) — CI Verificação | ✅ |
| B3 (4.3) — gdtoolkit Gate | 🔶 |

### ⬜ Camada 4 — Extensões de Processo (6 pendentes)

| Etapa | Nome | Arquivos | ⏱ | Depende |
|---|---|---|---|---|
| B2 (4.2) | CI Verificação [AUTO] | `.github/workflows/verification.yml` | 45m | Nenhuma | ✅ |
| B3 (4.3) | gdtoolkit Gate [SÊNIOR] | `tools/code_quality_ops.py`, `.gdlintrc` | 90m | Nenhuma | 🔶 |
| B4 (4.4) | Análises Específicas [SÊNIOR] | `tools/code_quality_ops.py` +9 ops | 2h | B3 |
| B5 (4.5) | Segurança Supply-Chain [SÊNIOR] | `tools/security_ops.py` +3 ops | 1h | Nenhuma |
| B6 (4.6) | agent_manage [SÊNIOR] | `tools/agent_ops.py` novo | 2h | Nenhuma |
| B7 (4.7) | Save Schema + Migração [SÊNIOR] | `tools/devsolo_ops.py` +2 ops | 1.5h | Nenhuma |
| B8 (4.8) | Dead-End Quest/Diálogo [SÊNIOR] | `tools/devsolo_ops.py` +2 ops | 1.5h | Nenhuma |
| B9 (4.9) | Documentação Automática [AUTO] | Rollup novo/docs | 45m | Nenhuma |

### Camadas 5-7 (Futuro — só com aprovação do Joab)

| Camada | Nome | Fatias |
|---|---|---|
| 5 | Gameplay | 5.1–5.8 |
| 6 | Profundidade de Engine | 6.1–6.8 |
| 7 | Polimento | 7.1–7.14 |

---

## 📊 MATRIZ DE CONFLITO

| AGENTE 01 ↓ / AGENTE 02 → | B2 CI | B3 gdtoolkit | B4 Análises | B5 Seg | B6 agent | B7 Save | B8 Dead-end | B9 Docs |
|---|---|---|---|---|---|---|---|---|
| A1 Namespaces | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| A2 ExecContext | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| A3 CONTRACTS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| A4 Intent Router | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| A5 Refatorações | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ |
| A6 Qualidade | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ |

> ✅ Sem conflito (arquivos diferentes) | ⚠️ Risco baixo — AGENTE 01 deve avisar no `SUTURE_ISSUES.md` se precisar MODIFICAR `security_ops.py` ou `devsolo_ops.py`

---

## 📋 7 REGRAS DE COLABORAÇÃO

### 1. Arquivos Exclusivos
Cada agente tem "posse" de arquivos. O outro pode LER, mas NÃO EDITAR sem autorização.

| Agente | Arquivos exclusivos |
|---|---|
| 🅰️ AGENTE 01 | `server.py`, `core/*`, `tools/deprecated.py`, `tools/registry_validation.py`, `tools/rollups.py` |
| 🅱️ AGENTE 02 | `tools/*_ops.py` (todos os módulos), `.github/*`, `docs/*`, `tests/*`, `.clinerules/*` |

### 2. Antes de Editar, Verificar
Consulte este documento. Se o arquivo é do outro agente → NÃO edita. Registra em `SUTURE_ISSUES.md`.

### 3. Checkpoint a Cada Etapa
- AGENTE 01: atualiza `ROADMAP_UNIFICADO.md`, `HANDOFF.md`, `NEXT_STEP.md`
- AGENTE 02: atualiza `.roadmap_progress.json`, `ROADMAP_UNIFICADO.md`, `HANDOFF.md`, `NEXT_STEP.md`

### 4. WIP Limit = 1
Uma etapa por vez. Só avança quando a atual estiver concluída, auditada e commitada.

### 5. Sutura só Descongela Entre Etapas
Mudanças na Zona de Sutura → `SUTURE_ISSUES.md` → Joab aprova → acontece entre etapas.

### 6. Commits Frequentes
1 commit por etapa concluída. Formato: `feat(agente-X-etapa-Y): descrição em português`. **NUNCA acumular +2 etapas sem commit.**

### 7. Handoff a Cada Etapa
`HANDOFF.md`: o que fez, o que NÃO fez, decisões tomadas, ⚠️ pontos de atenção para o outro agente.

---

## 🎯 ORDEM DE EXECUÇÃO

### Fase 1 — Preparação (CONCLUÍDA ✅)
- ✅ ROADMAP_UNIFICADO.md criado
- ✅ 23 arquivos redundantes deletados
- ✅ Arquivos de automação criados
- ⬜ COMMIT de tudo pendente

### Fase 2 — Execução Paralela (4-6 sessões)
```
🅰️ AGENTE 01                    🅱️ AGENTE 02
│                               │
├─ A1: Namespaces               ├─ B2: CI Verificação
├─ A2: ExecutionContext         ├─ B3: gdtoolkit Gate
├─ A3: DATA_CONTRACTS.md        ├─ B4: Análises Específicas
├─ A4: Intent Router            ├─ B5: Segurança Supply-Chain
├─ A5: Refatorações             ├─ B6: agent_manage
└─ A6: Qualidade MCP Spec       ├─ B7: Save Schema
                                 ├─ B8: Dead-End Quest
                                 └─ B9: Documentação Auto
```

### Fase 3 — Integração
| # | Ação | Quem |
|---|---|---|
| 1 | Revisar `SUTURE_ISSUES.md` | 👤 Joab |
| 2 | `validate_tool_registry_consistency()` | 🅰️ AGENTE 01 |
| 3 | `auditar.py` C1-C6 | 🅱️ AGENTE 02 |
| 4 | Merge final + tag de release | 👤 Joab |

---

## 📏 REGRAS DE NOMENCLATURA (PADRÃO MCP)

Baseado no SEP-986 e nas convenções oficiais do MCP:

| Regra | Exemplo |
|---|---|
| **snake_case** para tools | `scene_manage`, `node_manage` |
| **Verbo primeiro** (em rollups, `_manage`) | `asset_manage`, `script_manage` |
| **1-64 caracteres** | Máximo permitido pela spec |
| **Chars permitidos** | `a-z`, `0-9`, `_` |
| **# INTERNAL** para funções depreciadas | `# INTERNAL: usado por scene_manage` |
| **Anotações obrigatórias** | `destructiveHint`, `idempotentHint`, `openWorldHint` |

---

**Este documento é a FONTE ÚNICA DA VERDADE para o desenvolvimento do MCP Godot Agent.**
**Atualizado a cada etapa concluída por qualquer um dos agentes.**
**Em caso de dúvida ou conflito, o humano (Joab) decide.**
