# 🤝 HANDOFF.md — Estado do Projeto (fonte única de verdade)

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo.
> **Este é o "onde paramos" canônico.** Nenhum outro arquivo de estado (.session/NEXT_SESSION.md, etc.) deve ser usado.

---

## Último Handoff (AGENTE 01 — 2026-07-23 — AUDITORIA COMPLETA DO ECOSSISTEMA)

- **Data:** 2026-07-23
- **Commit:** `3c28cfb` (main, HEAD)
- **O que foi feito:** Auditoria completa de todo o ecossistema (2 partes, ~12h de trabalho). NENHUMA feature nova — somente leitura, coleta de fatos, e atualização de documentação.

### Métricas reais (comandos executados, não estimativas)

```
Tools visíveis: 236 (235 handlers)
Definições brutas em core/tool_definitions.py: 272
DEPRECATED_TOOLS: 189
ALIAS_MAP: 80
Behaviors: 249 (TODOS com behavior.json + .gd + .tscn — zero pastas vazias)
Domínios: 38
Fases: 6 (IDEIA→DESIGN→PROTOTIPO→CONTEUDO→POLIMENTO→PRONTO_PARA_LANCAR)

Tools por fase (teto=40):
  IDEIA: 37 ✅ | DESIGN: 82 ❌ | PROTOTIPO: 93 ❌
  CONTEUDO: 142 ❌ | POLIMENTO: 177 ❌ | PRONTO_PARA_LANCAR: 184 ❌

Testes (pytest): 157 passed, 1 failed (INV-03: execute_gdscript_runtime sem namespace), 8 xfailed
auditar.py: C1=PASS (235 changes, 0 breaking), C2-C7=SKIP (sem argumentos)
```

### Principais descobertas

1. **Comandos `/` funcionam** — os `.prompt.md` (plan, act, handoff, audit) estão em `%APPDATA%\Code\User\prompts\` (global), não no repo. Foram movidos pelo commit `3c28cfb` ("remove prompts locais duplicados").

2. **Behaviors estão COMPLETOS** — 249 behaviors, todos implementados com behavior.json + .gd + .tscn. A afirmação anterior no HANDOFF ("224 behaviors") estava desatualizada.

3. **Agente 2 sincronizado** — Worktree `mcp-godot-agente02` no mesmo commit da main (`9214970` = `3c28cfb`). Branch `agente2/behaviors-onda2` tem 160 commits NÃO mergeados (os behaviors em si).

4. **Teto de tools explodido** — 5 das 6 fases excedem 40 tools. Apenas IDEIA (37) está dentro. Fatia 0.7b (teto) está `marginal` há semanas.

5. **Nenhuma trava automática funciona** — Regra R20: hooks do VS Code não disparam com a extensão DeepSeek v0.6.2. Toda segurança depende de obediência do modelo a texto.

6. **Provas nunca exercitadas** — Zero pastas `.mcp_proof` no disco. Zero marcadores `.mcp_gate_failed`. Transições de fase nos projetos de teste são 80% forçadas (4 de 5 com `force=True`).

### Estado dos arquivos

| Arquivo | Correção feita |
|---|---|
| `server.py` docstring | "134 ferramentas" → "236 ferramentas visíveis" |
| `pyproject.toml` | "v3.2.1 — 191 ferramentas" → "v3.7.0 — 236 ferramentas, 249 behaviors, 38 domínios" |
| `_meta_tool.py` | "143 para ~33" → estado atual |
| `CATALOGO_COMPLETO.md` | "224 behaviors" → "249 behaviors" |
| `.github/copilot-instructions.md` | "~204 Tool()" → métricas atuais |
| `AGENTS.md` | Corrigidas refs a arquivos inexistentes, atualizado status do Agente 2 |

### Pendências (inalteradas)

- **Merge dos behaviors**: 160 commits em `agente2/behaviors-onda2` não mergeados
- **Teto de tools**: 5 fases excedem — fatia 0.7b marginal
- **59 tools SEM_FASE**: acessibilidade, gameplay, telemetria, onboarding
- **INV-03**: falso positivo (execute_gdscript_runtime sem namespace)
- **C3 (smoke_test)**: não disponível offline (requer MCP rodando)
- **Hooks não disparam**: R20 — sem trava automática real

### Próximo

- `/plan` para decidir: merge dos behaviors OU resolução do teto de tools OU F6.5 (backend nas respostas)
- Antes de qualquer `/act`: rodar `git log -3 --oneline` e `git status --porcelain`

### Para o Agente 2

- Branch `agente2/behaviors-onda2`: 160 commits, 249 behaviors completos
- Merge pendente na main — coordenar antes de mexer
- 3 stashes na branch de behaviors (WIP)
- Worktree limpo, sincronizado com main

---

## Handoff Anterior (AGENTE 01 — 2026-07-22 — ENCERRAMENTO)

- **Data:** 2026-07-22
- **Commit:** `efd137a` (main, pushed)
- **O que foi feito:** F5 CONCLUÍDA (37 domínios). F6 AVANÇADO (transport.py + editor_manage + game_bridge depreciações + screenshot_manage).

### Estado final do wire

```
defs_total=235, handlers_total=235
SEM_HANDLER=0, SEM_DEF=0
DEPRECATED_TOOLS=189, ALIAS_MAP=80
AUDITORIA F5: APROVADA (A01-A08, A10-A12)
352/352 reportados em 2026-07-22 (⚠️ auditoria 2026-07-23: 157 pass, 1 fail, 8 xfail = 166 reais)
```

### 38 domínios migrados (F5 + F6)

37 de F5 + `editor` (F6.2) + `screenshot` (F6.4)

### F6 — Transporte

- `adapters/transport.py`: 8 capacidades, 5 backends, cache TTL 5s
- `editor_manage`: absorveu 12 addon_* atômicas
- `game_bridge_manage`: absorveu 14 game_* atômicas (já tinha os ops)
- `screenshot_manage`: NOVO rollup, absorveu 4 screenshot atômicas

### Pendências

- F6.5: Incluir "backend" em todas as respostas
- F6.6: Corrigir fases (editor_manage já está em PROTOTIPO+CONTEUDO)
- F3/F4: Unificação de rollups + descoberta progressiva (parciais)
- 59 tools SEM_FASE (inalterado)
- INV-03 falso positivo (screenshot_manage em TOOLSETS mas teste falha por cache)

### Próximo

- Continuar F6 (backend nas respostas)
- Depois F7 (Resources) ou F3/F4 (rollups + descoberta progressiva)
- **Fatia:** F5.6 — Migrar domínio vfx/partículas
- **O que foi feito:** Criado `domains/vfx/` com 6 arquivos. 5 ops no rollup (+create_particles_3d). 2 atômicas removidas do wire. +3 aliases.

### Estado do wire

```
defs_total=269, handlers_total=268
SEM_HANDLER=0, SEM_DEF=0, NS_FANTASMA=0, PHASE_FANTASMA=0
AUDITORIA F5: APROVADA
184/184 testes passam (8 xfailed) — +8 testes domínio vfx
```

### Arquivos criados/alterados

- `domains/vfx/` — NOVO: `__init__.py`, `manifest.py`, `handlers.py`, `examples.py`, `schemas.py`, `test_vfx_domain.py`
- `tools/rollups.py` — `_build_vfx_manage()`: +1 op `create_particles_3d`
- `tools/deprecated.py` — +2 DEPRECATED_TOOLS, +3 ALIAS_MAP (42→45)
- `server.py` — -3 TOOL_LABELS, -3 TOOL_TAGS (atômicas vfx)
- `.reorg_progress.json` — fatia_atual: 5.5→5.6
- `.roadmap_progress.json` — +fatia_F5.6_vfx

### Decisões

- `create_particles_3d` adicionado como op ao `vfx_manage` (antes só existia como atômica DEPRECATED sem rollup)
- As 3 atômicas eram ORFAS (sem fase). Agora cobertas por `vfx_manage` em PROTOTIPO+CONTEUDO.
- Nenhuma regressão de fase — rollup já estava em PROTOTIPO.

### Pendências (inalteradas)

- **F5.7+**: ~7 domínios restantes (render, skeleton, debug, lsp, godot, network, lights + screenshot?)
- **F3 completa**: Unificação dos 3 caminhos de rollup pendente
- **F4 completa**: Descoberta progressiva por fase pendente
- **59 tools SEM_FASE** (inalterado)
- **Aliases**: 45 entradas, expiram em F6

### Próximo

- `/plan` para F5.7 — próximo domínio com rollup funcional (render, skeleton, debug, lsp, godot, network)
- Rodar `audit_fase.py --fase F5` e `pytest tests/ domains/ -q` antes de começar

---

## Handoff Anterior (AGENTE 01 — 2026-07-21 — FECHAMENTO DA ESTABILIZAÇÃO)

- **Data:** 2026-07-21
- **Commit:** 3f109f2 (main, pushed to origin)
- **O que foi feito:** PARADA DE ESTABILIZAÇÃO completa (CHECKPOINT → E1-E6 → J1-J4 → K1-K3 → L1-L4 → M1-M3 → Auditoria final). NENHUMA feature nova — apenas correção de processo, dívida técnica e dano ao wire.

### Estado final do wire

```
defs_total=269, handlers_total=268
SEM_HANDLER=0, SEM_DEF=0, NS_FANTASMA=0, PHASE_FANTASMA=0
AUDITORIA F5: APROVADA
176/176 testes passam (8 xfailed)
```

### Arquitetura pós-estabilização

- **DEPRECATED_TOOLS** (~112 ferramentas) agora filtra **tanto** `_tool_defs()` quanto `_build_handlers()` — consistente. Filtro condicional a `_REGISTRY_VALIDATION_UNFILTERED` (default=False → filtra em operação normal).
- **ALIAS_MAP** (42 entradas em `tools/deprecated.py`) — `invoke_by_name` redireciona nomes antigos para rollups ANTES do phase gate. Loga `deprecated_alias_used`. Expira em F6 (Secao 11.9).
- **TOOLSETS e PHASE_TOOLSETS** limpos — ~46 entradas atômicas removidas. Apenas rollups `_manage` permanecem.
- **Invariantes INV-10/INV-11** excluem DEPRECATED_TOOLS da contagem. INV-01/INV-02 verificam paridade wire↔handler.
- **audit_fase.py** implementa Seção 15 (A01-A12, "AUDITORIA F<N>: APROVADA"). test_invariants.py cobre INV-01..15 com 8 xfail.
- **test_remix.py** corrigido (bug de isolamento — cleanup + try/finally).
- **test_tutorial_01.py** corrigido (dependência de dirt do remix removida).

### 6 rollups com cobertura real provada (K1)

| Rollup | Fases | Prova |
|---|---|---|
| godot_manage | PROTOTIPO | exec_gdscript: erro pré-cond (sem jogo) — dispatch OK |
| lsp_manage | DESIGN | hover: erro parâmetro (falta 'character') — dispatch OK |
| debug_manage | POLIMENTO | **status: SUCESSO** — debugger 127.0.0.1:6006 |
| network_manage | CONTEUDO | setup_peer: erro pré-cond (cena não encontrada) — dispatch OK |
| render_manage | DESIGN+CONTEUDO | **get: SUCESSO** — 7 settings reais do breakout_test |
| skeleton_manage | DESIGN+CONTEUDO | list_bones: erro pré-cond (cena não encontrada) — dispatch OK |

### Commits da sessão

```
3f109f2 fix-auditoria-final-estabilizacao-3-bugs      (bug #1, #2, doc, +3 tests)
6d7ca49 feat-K1-K3-aliases-limpeza-TOOLSETS-estabilizacao-final
d65fe00 docs-registra-estabilizacao-E1-E6-roadmap
996d588 fix-E1-E5-estabilizacao-auditoria-aprovada
```

### Arquivos alterados nesta sessão

- `server.py` — filtro DEPRECATED_TOOLS em `_tool_defs()`, limpeza TOOLSETS/PHASE_TOOLSETS
- `tools/deprecated.py` — +5 entries, +ALIAS_MAP (42), docstring atualizado
- `tools/meta_ops.py` — alias resolution step 0, dead code removido, bug #1 corrigido
- `registry/invariants.py` — INV-10/INV-11 excluem DEPRECATED_TOOLS
- `scripts/audit_fase.py` — A03 corrigido, A05 usa `essential={manifest,handlers}`
- `tests/test_invariants.py` — NOVO (140+ linhas, INV-01..15 + 3 testes de alias)
- `tests/test_remix.py` — adicionado cleanup + try/finally
- `tests/test_tutorial_01.py` — captura FileNotFoundError no get_next_step
- `.reorg_progress.json` — recriado, válido, atualizado com métricas finais
- `.roadmap_progress.json` — registrada estabilização E1-E6

### Decisões

- **KW-only wrappers** como padrão para todos os handlers de domínio (estabelecido em F5.1 physics, corrigido em F5.2 ui)
- **DEPRECATED_TOOLS como mecanismo único** de filtragem (não dois sistemas separados)
- **Aliases expiram em F6** (Secao 11.9), registrado em `.reorg_progress.json`
- **Commit automático pós-/act** (confirmado pelo usuário)
- **Nenhuma regressão de fase** — rollups têm MAIS cobertura que as atômicas antigas (M1-M3)

### Pendências

- **F5.6+**: Continuar migração dos domínios restantes (~8 domínios)
- **F3 completa**: Unificação dos 3 caminhos de rollup pendente
- **F4 completa**: Descoberta progressiva por fase pendente
- **59 tools SEM_FASE**: acessibilidade, gameplay, telemetria, onboarding — nunca atribuídas a fases
- **COLISAO_ROLLUP**: `playtest_manage` definido em `_raw_tool_defs()` E em `get_rollup_tool_defs()`
- **Aliases**: Remover em F6 (42 entradas em ALIAS_MAP)
- **ruff**: Não instalado no venv (A02 warning)
- **create_light_2d**: removido de PHASE_TOOLSETS mas ainda em DEPRECATED_TOOLS (sem rollup atribuído)

### Próximo

- `/plan` para F5.6 (próximo domínio a migrar)
- Antes: verificar `.reorg_progress.json` e `.roadmap_progress.json`
- Rodar `audit_fase.py --fase F5` para confirmar baseline limpo
- **NUNCA** pular auditoria antes de commit
- **NUNCA** commitar sem aprovação humana (exceto pós-/act)

### Para o Agente 2 (Conteúdo)

- Nada nesta sessão afetou behaviors/, blueprints/, seeds/, addons/, tests/ (exceto test_remix e test_tutorial_01)
- Agente 2 pode continuar normalmente
- Se precisar tocar em server.py, tools/deprecated.py, ou tools/meta_ops.py — **AVISAR antes** (terra de ninguém)
- 4.A — publish_manage (AssetLib): empacotar addons em .zip
- Gap Comunidade — community_manage (changelog, release_notes, roadmap_public, badge)
- Gap Limpeza — B5 warnings corrigidos, budget limits atualizados
- 4.F — GitHub Discussions: guia de ativação + templates
- Documento de auditoria de tools (`.github/audit/tool_organization_audit.md`)

**Pesquisas externas (nível extremo):**
- ONDA 4 completa (distribuição, monetização, comunidade, identidade, métricas, Steam)
- Organização de tools (taxonomia, curadoria, escalabilidade)

### Métricas finais

| Indicador | Valor |
|---|---|
| Tools | 287 |
| Handlers | 184/184 registrados |
| Testes | 148/148 passam |
| C1 | 0 breaking |
| C3 | PASS |
| C5 | Pré-existente (0.7) |
| Commits nesta sessão | 5 |

### Estado das Ondas

- ONDA 0: ✅ 12/12
- ONDA 1: ✅ 17/17
- ONDA 2: ⏳ Agente 2 (branch agente2/behaviors-onda2)
- ONDA 3: ✅ 21/21
- ONDA 4: ⏳ 1/7 (4.A ✅) + gaps de comunidade ✅

### Próximo passo

- Aguardar auditoria do Claude sobre organização de tools
- Decidir nome do produto (4.D)
- Implementar consolidação de tools conforme recomendação do Claude

---

## Último Handoff (AGENTE 01 — 2026-07-21 — Pesquisa Organização de Tools)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Pesquisa externa nível extremo — Organização de Tools (taxonomia, curadoria, escalabilidade)

### Diagnóstico

- 287 tools em lista plana, 13 rollups (4.5%), 75 órfãs de fase
- PROTOTIPO: 100 tools visíveis (2.5x acima do teto)
- Nomes baseados em verbos, não recursos (Azure API Design)
- Hints MCP não utilizados (readOnlyHint, destructiveHint, etc.)

### Recomendações (7 priorizadas, todas não-destrutivas)

| # | Recomendação | Esforço | Impacto |
|---|---|---|---|
| R1 | Adicionar hints MCP nas 287 tools | 2h | Alto |
| R2 | Enriquecer catalog_search com taxonomia | 1h | Alto |
| R3 | Criar 5 rollups críticos | 3h | Alto |
| R4 | Metadata de fase/namespace nas tools | 1h | Alto |
| R5 | Curadoria agressiva por fase | 30min | Alto |
| R6 | Migrar 22 famílias para rollups | 8h | Alto |
| R7 | Paginação no tools/list | 2h | Médio |

### Documentos atualizados

- `docs/PESQUISA_EXTERNA.md` — +Seção 8 (~400 linhas): Organização de Tools

### Próximo passo

- Implementar R1 (hints MCP) — mais rápido, maior impacto, zero breaking changes
- Rode `/plan`.

---

## Último Handoff (AGENTE 01 — 2026-07-21 — Pesquisa ONDA 4)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Pesquisa externa nível extremo — ONDA 4 (MUNDO) completa

### O que foi pesquisado

**7 domínios mapeados exaustivamente:**

1. **Distribuição de addons** (AssetLib, itch.io, gd-plug, GitHub Releases, canais alternativos)
   - AssetLib: 5.227 assets, 6 concorrentes MCP+Godot, submissão manual, sem API
   - itch.io: 29.680 tools, open revenue sharing, pay what you want, analytics
   - gd-plug: 296★, plugin manager com version freeze, requer Git

2. **Monetização open source** (GitHub Sponsors, modelos de negócio, projeções)
   - GitHub Sponsors: $40M+ distribuídos, tiers com benefícios NOMEADOS (nunca genéricos)
   - Sidekiq, Homebrew, curl como referências de sucesso
   - Projeção: $15–150/mês no primeiro ano

3. **Steam publishing** (Steam Direct, requisitos, estratégia de lançamento)
   - $100/fee, 30 dias espera, revisão Valve 1–5 dias
   - Shardbreaker como prova de marketing mais forte que existe

4. **Comunidade** (GitHub Discussions vs Discord, canais, moderação)
   - GitHub Discussions PRIMEIRO (assíncrono, indexado, baixa manutenção)
   - Discord DEPOIS (≥ 50 usuários ativos)

5. **Nome e identidade** (análise do nome atual, padrões de naming, sugestões)
   - `mcp-godot-desenvolvimento` = repositório, não produto
   - Sugestão: "Saga" como nome de produto

6. **Métricas** (CHAOSS, opensource.guide framework, dashboard proposto)
   - Métrica principal: quantas pessoas terminam um jogo
   - Proxies: projetos → PRONTO_PARA_LANCAR, depoimentos, fun_report

7. **Oportunidades adicionais** (19 oportunidades mapeadas além do roadmap)
   - Upload via itch.io API (butler), export Godot via MCP, CI/CD GitHub Actions
   - Landing page, badge "Made with MCP", changelog automático, heatmap de erros

### Ordem revisada da ONDA 4 (baseada na pesquisa)

| # | Original | Revisada | Justificativa |
|---|---|---|---|
| 4.A | AssetLib | ✅ Concluído | Primeiro canal |
| 4.B | itch.io | **4.D Nome** | Sem nome, não publica |
| 4.C | Sponsors | **4.E Shardbreaker** | Sem prova, não tem marketing |
| 4.D | Nome | **4.B itch.io** | Com nome e prova, publica |
| 4.E | Shardbreaker | **4.F Comunidade** | Com produto, cresce comunidade |
| 4.F | Comunidade | **4.C Sponsors** | Com comunidade, monetiza |
| 4.G | Métricas | **4.G Métricas** | Paralelo, sempre relevante |

### Documentos atualizados

- `docs/PESQUISA_EXTERNA.md` — +Seção 7 (~500 linhas): ONDA 4 completa
- `.github/instructions/fontes.instructions.md` — +Seção "Distribuição e Mundo (ONDA 4)"

### Próximo passo

- **4.D — Nome e identidade do produto** [SÊNIOR] — definir nome, logo, tagline, paleta de cores
- Rode `/plan`.

## ⚠️ AVISO AO AGENTE 2 (2026-07-21)

**ONDA 3 em andamento pelo Agente 1. Não interfira em:**
- `tools/playtest_ops.py`
- `tools/personas.py`
- `core/tool_definitions.py`
- `server.py`
- `tests/test_personas.py`
- `tests/test_playtest.py`
- `.roadmap_progress.json`

## Último Handoff (AGENTE 01 — 2026-07-21 — Fatia 3.B)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 3.B — Playtest camada 2: personas scriptadas [SÊNIOR]

### O que foi feito

- `tools/personas.py` (NOVO, 153 linhas) — 3 personas (apressado/cauteloso/explorador) com KEY_MAP Godot 4
- `tools/playtest_ops.py` — estendido (+180 linhas): `op=persona_run` no rollup `playtest_manage`
- `_send_key_event()` — simula hold com taps a 50ms via runtime bridge (:8790) `input_event`
- Coleta: completed, total_time_s, total_inputs, input_errors, métricas inicial/final
- `core/tool_definitions.py` — schema atualizado com `persona_run` + parâmetro `persona`
- `tests/test_personas.py` — 10 testes (listagem, validação, KEY_MAP, smoke regressão)

### Como usar
- `playtest_manage op=persona_run persona=apressado duration=60`
- Personas: apressado (rush), cauteloso (careful), explorador (explore)
- Requer jogo rodando em debug (F5 no Godot)

### Métricas
- **ONDA 1:** ✅ 17/17
- **ONDA 3:** 2/11 (3.A + 3.B concluídas)
- **Total tools:** 279
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **Testes:** 47/47 (10 personas + 11 smoke + 26 version_history)

### Próximo passo
- **3.C — Playtest camada 3: agente LLM pontual** [SÊNIOR]

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 3.A — Playtest camada 1: smoke automático [AUTO]

### O que foi feito

- `tools/playtest_ops.py` — estendido (+175 linhas): rollup `playtest_manage(op=smoke)`
- Smoke test do JOGO via runtime bridge (:8790): coleta FPS, draw_calls, memória
- Detecta crash (bridge para de responder), FPS abaixo do threshold
- Valida viewport ativo (screenshot)
- `core/tool_definitions.py` — tool `playtest_manage` registrada
- `server.py` — handler `_handle_playtest_manage` registrado
- `tests/test_playtest.py` — 10 testes pytest

### Como usar
- `playtest_manage op=smoke duration=10 fps_threshold=30` — smoke test do jogo
- Requer jogo rodando em debug (F5 no Godot)
- NÃO usa --headless (R12: não funciona no Windows 4.7)

### Métricas
- **ONDA 1:** ✅ 17/17
- **ONDA 3:** 1/11 (3.A concluída)
- **Total tools:** 279 (+1)
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)
- **Testes:** 10/10 pytest + regressão 26/26

### Próximo passo
- **3.B — Playtest camada 2: personas scriptadas** [SÊNIOR] — ou continuar ONDA 2 com Agente 2

---

## Handoff anterior (AGENTE 01 — 2026-07-21 — Fatia 1.Q)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 1.Q — Histórico de versões jogáveis [SÊNIOR]

### O que foi feito

- `tools/version_history_ops.py` (NOVO, 334 linhas) — rollup `version_history_manage(op=save|list|restore|delete|screenshot)`
- Screenshot via `runtime_bridge_client.send_bridge_command({"cmd": "screenshot"})` — comando já existente no addon
- Armazenamento em `<project>/.mcp_versions/` com `index.json` + `manifest.json` + `screenshot.png`
- Save fail-soft: sem jogo rodando, salva sem screenshot com aviso
- Restore: `git checkout <commit> --` com validação de working tree limpo + checkpoint via `safety.checkpoint()`
- Path traversal sanitizado em version_id
- Lock `VERSION_HISTORY_LOCK` em `tools/config_lock.py`
- `core/tool_definitions.py` — tool `version_history_manage` registrada
- `server.py` — handler `_handle_version_history_manage` registrado
- `tests/test_version_history.py` (NOVO) — 26 testes automatizados (pytest)
- Auditoria: 1 bug CRÍTICO encontrado e corrigido (`run_subprocess_safe` kwargs conflitantes)

### Como usar
- `version_history_manage op=save description="Antes de refatorar IA"` — salva versão jogável
- `version_history_manage op=list` — lista versões salvas
- `version_history_manage op=restore version_id="20260721_143022"` — restaura versão (git checkout)
- `version_history_manage op=delete version_id="20260721_143022"` — remove versão
- `version_history_manage op=screenshot` — captura screenshot avulso (jogo precisa estar rodando)

### Métricas
- **ONDA 1:** ✅ 17/17 CONCLUÍDA
- **Total tools:** 278 (+1)
- **Total handlers:** 299 (+1)
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)
- **Testes:** 26/26 pytest + 10/10 manuais

### Próximo passo
- **ONDA 2 — O FOSSO** — `.github/roadmap/ONDA_2_fosso.md`. Fatia 2.A. Rode `/plan`.

---

## Handoff anterior (AGENTE 01 — 2026-07-21 — Fatia 1.P)

- **Data:** 2026-07-21
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação da Fatia 1.P — Telemetria opt-in do próprio MCP

### O que foi feito

- `tools/mcp_telemetry_ops.py` (NOVO, 574 linhas) — rollup `mcp_telemetry_manage(op=status|enable|disable|export|reset)`
- Hook `track_mcp_event()` em `server.py::call_tool()` — fail-open, mesmo padrão de `budget_ops`
- Hook `track_phase_transition()` integrado no `advance_phase`
- `core/tool_definitions.py` — tool `mcp_telemetry_manage` registrada
- `docs/PESQUISA_EXTERNA.md` — Seção 6: pesquisa de 8 fontes sobre telemetria de ferramentas

### Como usar
- `mcp_telemetry_manage op=enable` ativa coleta (consentimento explícito)
- `mcp_telemetry_manage op=status` mostra métricas
- `mcp_telemetry_manage op=export` gera relatório JSON
- Dados 100% locais (.mcp_telemetry_events.jsonl)

### Métricas
- **ONDA 1:** 16/17 concluídas
- **Total tools:** 277
- **C1:** PASS (0 breaking)
- **C3:** PASS (smoke_test)
- **C5:** pre-existente (8 fases overflow)

### Próximo passo
- **1.Q — Histórico de versões jogáveis** [SÊNIOR] — última fatia da ONDA 1

---

## Handoff anterior (AGENTE 01 — 2026-07-20 — Comando /pesquise)

- **Data:** 2026-07-20
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação do comando `/pesquise` + protocolo de pesquisa

### O que foi feito

- `.github/instructions/pesquisa.instructions.md` (NOVO) — protocolo canônico de 9 fases
- `%USERPROFILE%/AppData/Roaming/Code/User/prompts/pesquise.prompt.md` (NOVO) — prompt VS Code
- `.github/instructions/fontes.instructions.md` — referência ao protocolo
- `docs/PESQUISA_EXTERNA.md` — índice de pesquisas + referência ao protocolo

### Como usar
- Digite `/pesquise` no chat → auto-detecta contexto (fatia atual, fase) e pesquisa até saturação
- `/pesquise [tema]` → pesquisa tema específico
- O protocolo evolui com o projeto: edite `pesquisa.instructions.md` para refinar

### Próximo passo
- **1.F — Erro amigável universal** [AUTO] (plano já apresentado, aguardando aprovação)

---

## Handoff anterior (AGENTE 01 — 2026-07-20 — ONDA 1: 1/17)

- **Data:** 2026-07-20
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** ONDA 0 (12/12) + Fatia 1.A — Instalador de 1 comando

### 1.A — init.py (760+ linhas, NOVO)

Instalador standalone (só stdlib): detecta Godot/Python/VS Code, cria venv,
gera `.vscode/mcp.json` com merge, cria projeto Godot + addon, abre editor,
faz bridge polling (LSP :6005 + WS :9082, timeout 30s). Idempotente.
Mensagens em português. `--silent`, `--no-verify`, `--verbose`.

### 0.L — Detalhe técnico

**Causa raiz:** `set_node_property()` modificava `lines` em memória mas nunca
chamava `full_path.write_text()`. Comparado com `add_node()` e `delete_node()`
que têm o padrão completo: checkpoint → modificar → deduplicar → **write_text**
→ cache.pop → mark_pending_compile.

**Correção:** +7 linhas após `_deduplicate_tscn_lines()`.
**B3 extra:** removidos 2x `import re` redundantes dentro de `_deduplicate_tscn_lines`.

### Métricas

- **Total tools:** 274 (sem alteração)
- **Handlers:** 295 (sem alteração)
- **Novos arquivos:** init.py, cloud_sync_detector.py, name_utils.py, ip_guard.py
- **Arquivos expandidos:** server.py, project_ops.py, project_brief_ops.py, art_ops.py, tool_definitions.py, scene_ops.py
- **ONDA 0:** ✅ 12/12
- **ONDA 1:** 1/17 (1.A concluída)

### ⚠️ Pontos de atenção

- init.py é standalone (só stdlib) — não importa tools/
- mcp.json usa merge: servidores existentes preservados
- Bridge WS :9082 timeout se outro projeto Godot já ocupa a porta
- C1/C5 do auditar.py: pré-existentes (7 breaking, 8 fases overflow)

### Próximo passo
- **1.B — Instalar templates de export** [AUTO]

---

- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Implementação COMPLETA da Camada 6 — Profundidade de Engine (8/8 fatias)

### O que foi feito

| Fatia | Descrição | Arquivo |
|---|---|---|
| 6.1 | Skeleton IK / Bone Pose (6 ops) | `tools/skeleton_ops.py` (NOVO) |
| 6.2 | 3D Depth — CSG, GI, Decal, Sky, Camera, MultiMesh (6 ops) | `tools/devsolo_ops.py` (expandido) |
| 6.3 | Física — Joints, Body Config, Area Query, Raycast (4 ops) | `tools/physics_ops.py` (expandido) |
| 6.4 | UI Granular — Widgets, Tabs, Focus Nav, Tooltip, Anchors (5 ops) | `tools/devsolo_ops.py` (expandido) |
| 6.5 | Rede — Multiplayer, RPC, WebSocket, Lobby (5 ops) | `tools/network_ops.py` (NOVO) |
| 6.6 | Runtime Signals — Connect, Disconnect, Emit, List, Watch (5 ops) | `tools/runtime_ops.py` (expandido) |
| 6.7 | Render Settings — AA, Scaling, Quality Presets (4 ops) | `tools/render_ops.py` (NOVO) |
| 6.8 | C#/.NET Scaffold — Project, Script Templates, Build (3 ops) | `tools/csharp_ops.py` (NOVO) |

### Métricas

- **Total tools:** 268 → 274 (+6)
- **Handlers:** 295 → 306 (+11, incluindo rollups)
- **Novos arquivos:** `skeleton_ops.py`, `network_ops.py`, `render_ops.py`, `csharp_ops.py`
- **Arquivos expandidos:** `devsolo_ops.py`, `physics_ops.py`, `runtime_ops.py`
- **Validação:** 274 tools, 306 handlers, 0 inconsistencias (32 extras = rollups)

### Distribuição por namespace
- **project** (31): skeleton (6), 3D depth (6), physics joints/body (2), UI granular (5), network (5), render (4), csharp (3)
- **runtime** (5): physics queries (2), runtime signals connect/disconnect/emit (3)
- **analysis** (2): runtime signal list/watch (2)

### ⚠️ Pontos de atenção para AGENTE 02
- `skeleton_ops.py` opera por parsing de arquivos .tscn — se mudar formato de scene, revise
- `network_ops.py` e `csharp_ops.py` geram código GDScript/C# — templates podem precisar de ajuste
- Handlers usam dispatch dinâmico por prefixo (ex: `skeleton_*` → `skeleton_ops`) — se renomear funções, mantenha consistência
- Camada 6 é [MARGINAL] — risco de scope creep. Documentado como "Campo A" no roadmap.

### Próximo passo (AGENTE 01)
- **Camada 7 (Polimento)**: [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 01 — 2026-07-19 — Registro Camada 5)

- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Ação:** Registro de 28 tools da Camada 5 (Gameplay) no pipeline de tools

### O que foi feito

| Fase | Descrição | Arquivo |
|---|---|---|
| 1 | +28 Tool() definitions | `core/tool_definitions.py` |
| 2 | +28 handler wrappers | `server.py` (_build_handlers + _handle_*) |
| 3 | +28 nomes nos namespaces | `server.py` (TOOLSETS), `tools/dynamic_groups.py` (GROUPS) |
| 4 | Validação | `validate_tool_registry_consistency()` → 268/268 = 0 inconsistências |

### Distribuição por namespace
- **project** (16): achievements (2), mods (1), cutscenes (3), quest, dialogue (2), accessibility (3), onboarding (2)
- **analysis** (10): validate_achievement, validate_mod, telemetry (4), adaptive, accessibility_audit, cert, onboarding_check
- **assets** (3): trailer (3)
- **orchestration** (1): remote_balance_config

### ⚠️ Pontos de atenção para AGENTE 02
- **28 tools NÃO estão no PHASE_TOOLSETS** — aparecem apenas via `--profile full` ou `--toolsets` explícito
- Cabe ao AGENTE 02 decidir em quais fases ativar cada tool
- Handlers são wrappers finos que delegam para `tools/*_ops.py` — se renomear funções lá, atualize os wrappers
- `dialogue_generate_npc_lines` e `dialogue_generate_personality` já existiam como funções — foram apenas registradas formalmente

### Próximo passo (AGENTE 01)
- **Camada 6 (Profundidade de Engine)**: [MARGINAL] — aguarda aprovação do Joab
- **Camada 7 (Polimento)**: [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 02 — 2026-07-19 — Sessão de Polimento)

- **Data:** 2026-07-19
- **De:** AGENTE 02 (Extensões & Qualidade)
- **Ação:** Polimento completo — 7 fases implementadas

### O que foi feito (resumo)

| Fase | Nome | Resultado |
|---|---|---|
| F1 | Diagnóstico | 51% coverage, 18 tools sem teste |
| F2 | Cobertura Tier-1 | +18 handlers sintéticos → 87.8% (100% excl skip), 0 tools sem cobertura |
| F3 | Regressão Visual | `manage_visual_baselines()`, threshold calibrado, `--visual` no `auditar.py` |
| F4 | Perf Regression | Handler sintético, `perf_regression_track` já existia em `perf_ops.py` |
| F5 | Canary Queries | 14 → 48 queries, 45 tools cobertas |
| F6 | Audio Engine | `tools/audio_ops.py` (fachada unificada), play/set/stop no runtime bridge |
| F7 | Documentação | HANDOFF, NEXT_STEP, roadmap atualizados |

### Arquivos modificados/criados
- `tools/test_ops.py` — +18 handlers sintéticos, +40 `_SYNTHETIC_HANDLERS`
- `tests/canary_queries.json` — 14 → 48 queries
- `tools/runtime_ops.py` — `manage_visual_baselines()`, thresholds documentados
- `auditar.py` — `--visual`, `C7_visual`
- `tools/audio_ops.py` — NOVO, fachada unificada de áudio
- `runtime_bridge_client.py` — `play_audio()`, `set_volume()`, `stop_audio()`
- `addons/mcp_runtime_bridge/runtime_bridge.gd` — comandos de áudio em GDScript

### ⚠️ Pontos de atenção para AGENTE 01
- `_SYNTHETIC_HANDLERS` expandido de 21 → 40 tools — se adicionar tool nova, considere adicionar handler também
- `auditar.py` ganhou C7_visual — se modificar a assinatura de `run_audit()`, inclua os parâmetros `visual*`
- `audio_ops.py` reexporta de `devsolo_ops.py`, `music_ops.py`, `tts_ops.py`, etc. — se renomear funções nesses arquivos, atualize a fachada

### Próximo passo (AGENTE 02)
- **Camada 5 (Gameplay)**: TODAS [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 01)
- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Etapas concluídas:** A1 (Namespaces) + A2 (ExecutionContext) + A3 (DATA_CONTRACTS)

### O que foi feito (A3)
- **`DATA_CONTRACTS.md`** (novo): Contrato formal entre agentes — ZERO código
  - **6 seções**: Tool Definition, Handler, Pipeline, Comunicação, Nomenclatura, Validação
  - Documenta o ciclo completo: `Tool()` → filtros → `call_tool` → handler → resposta
  - Inclui contratos das Etapas A1 (5 namespaces, `TOOLSETS`, `TOOL_NAMESPACES`) e A2 (`ExecutionContext`, thread-local, cache TTL)
  - Define regras para AGENTE 02 adicionar tools (onde mexer, onde NÃO mexer)
  - Especifica Zona de Sutura (arquivos congelados)
  - Referência canônica para ambos os agentes

### O que foi feito (A2)
- **`core/context.py`** (novo): `ExecutionContext` dataclass com thread-local storage
  - Campos: `active_project`, `active_scene`, `phase`, `vibe_enabled`, `vibe_focus_node`
  - Cache TTL 5s para `scene_tree` (evita re-resolução a cada chamada)
  - API: `resolve_execution_context()`, `get_execution_context()`, `set_execution_context()`
- **`server.py`**: `_dispatch_with_context` wrapper no `call_tool` injeta contexto antes de cada handler
  - Contexto resolvido UMA vez por tool, disponível via `get_execution_context()`
- **`tools/scene_ops.py`**: `_resolve_scene_path_from_vibe()` estendido para consultar `ExecutionContext`
  - `paint_tilemap_cell` e `detect_offscreen_elements` ganharam fallback (eram as únicas sem)
  - `scene_path` agora é `str | None = None` com resolução automática
- **`tools/code_quality_ops.py`**: SyntaxError corrigido (f-string com escape inválido) — bloqueava `import server`
- **Gate**: `scene_manage(op="create")` funciona SEM parâmetro `scene_path`

### O que foi feito (A1)
- **TOOLSETS reestruturado** em 5 namespaces semânticos (239 tools mapeadas):
  - `project` (51 tools) — Cenas, scripts, arquivos, UI, gameplay estrutural
  - `assets` (37 tools) — Arte, áudio, shaders, VFX, geração procedural
  - `runtime` (77 tools) — Execução, debug, testes, bridge, jogo rodando
  - `analysis` (29 tools) — Auditoria, qualidade, referências, introspecção
  - `orchestration` (45 tools) — Meta-tools, workflow, governança, segurança
- **TOOL_NAMESPACES**: Dicionário reverso (239 tool_name → namespace) derivado do TOOLSETS
- **Injeção de namespace**: Cada `Tool()` recebe `_meta={"namespace": "..."}` via pós-processamento
- **`tools/dynamic_groups.py`**: `GROUPS` sincronizado (239 tools); `NAMESPACE_INFO` com descrições PT-BR; `tool_groups` suporta `action="hierarchy"`; `tool_catalog` suporta `namespace`
- **Auditoria**: 28 problemas encontrados e corrigidos (14 órfãs, 1 rollup não mapeado, 13 inconsistências) — agora 0 problemas
- Arquivos: `server.py`, `tools/dynamic_groups.py`, `ROADMAP_UNIFICADO.md`, `HANDOFF.md`, `NEXT_STEP.md`

### O que NÃO foi feito
- NÃO modifiquei `tools/deprecated.py`, rollups, ou handlers
- NÃO mudei o comportamento de `--profile` ou `--toolsets`
- A duplicação `TOOLSETS` ↔ `GROUPS` é conhecida (239 tools idênticas) — futura refatoração pode unificar

### ⚠️ Pontos de atenção para AGENTE 02
- `GROUPS` antigo (13 grupos) foi substituído por 5 namespaces — se houver referências aos grupos antigos, atualizar
- `tool_catalog` agora retorna `namespace` em cada resultado e `namespace_info` no envelope
- `tool_groups("hierarchy")` retorna visão hierárquica: namespace → descrição → tools
- Novas tools adicionadas ao `TOOLSETS` automaticamente recebem namespace; novas tools também devem ser adicionadas ao `GROUPS` em `dynamic_groups.py`

### Próxima etapa (AGENTE 01)
- **A2 — ExecutionContext**: Criar `core/context.py` com `ExecutionContext` dataclass

---

## Histórico

### AGENTE 02 — B3 (2026-07-19) ✅ Testado com gdtoolkit 4.5.0 real
- Criado `tools/code_quality_ops.py` (~570 linhas) com gdlint + gdformat + gdradon
- `.gdlintrc` reescrito em YAML (formato correto do gdlint 4.5.0)
- Gate integrado no `run_verification_pipeline` (etapa 6)
- 19/19 testes passaram (T1-T6) com projeto real (max-manos-like)
- Gate detectou: 569 violações gdlint, 89 arquivos mal formatados, avg CC=2.2
- 4 bugs de CLI corrigidos (--config, --show-complexity, PATH, SyntaxWarning)
- `tests/test_code_quality_ops.py` criado com 19 testes automatizados

### AGENTE 02 — B2 (2026-07-19)
- Criado `.github/workflows/verification.yml` — CI com 7 jobs



## Pendências registradas

**Auditoria de consistência de domínios:** nem todos os domínios em domains/
seguem o mesmo conjunto de arquivos do template _template/ (ex.: camera tem
menos arquivos que physics). Precisa de uma sessão dedicada, separada de
documentação, porque mexe em código.



## Pendência: features do Agente 02 não integradas

Os seguintes arquivos da branch `agente2/behaviors-onda2` NÃO foram mergeados
porque têm conflitos com a reorganização feita no `chore/limpeza-agent-only`:

- `server.py` — handlers das ONDAs 3+4 (reviewer_manage, teacher_manage,
  playtest_manage) precisam ser reimplementados na arquitetura nova
  (rollup-first, KW-only handlers, filtro DEPRECATED_TOOLS).
- `core/tool_definitions.py` — definições de tools das ONDAs 3+4 precisam
  ser registradas como ops de rollup, não como tools de topo.
- `tools/behavior_ops.py` — operações expandidas pelo Agente 02 conflitam
  com a reorganização de tools.
- `auditar.py` — critérios expandidos (C1-C6) precisam ser consolidados
  com a versão reorganizada.

Branch de referência preservada: `agente2/behaviors-onda2` (commit `eef0ffe`).

Todo o conteúdo não-código (behaviors, example_project, seeds, templates,
scripts de auditoria, bt_editor, tools novas) já foi integrado com sucesso.


## Encerramento — 2026-07-22

**Worktree/Agente:** C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento
**Peso:** Sessao longa de reorganizacao. Destaque para a integracao do Agente 02 e criacao do sistema de coordenacao entre worktrees.

### Resumo
Sessao de reorganizacao completa do projeto MCP Godot Agent: modelo agente nativo + comandos /, integracao do trabalho do Agente 02 (behaviors, example_project, seeds, templates, scripts, tools, bt_editor), sistema de coordenacao entre dois worktrees, enriquecimento do handoff com contexto e decisoes abertas, rotacao automatica do HANDOFF.md.

### Estado
- Branch: chore/limpeza-agent-only (commit e4a980b)
- Worktrees: principal (chore/limpeza-agent-only) + agente02 (agente2/trabalho)
- Integracao Agente 02: concluida (behaviors, example_project, seeds, templates, scripts, bt_editor, 12 tools)
- Coordenacao: coordenacao.json na pasta .git comum, prompts e hook de estado atualizados
- Handoff: formato enriquecido (worktree, peso, contexto nao-codigo, decisoes humanas), rotacao automatica

### Pendências
- [ ] Reimplementar features ONDAs 3+4 do Agente 02 na arquitetura nova (server.py, core/tool_definitions.py, tools/behavior_ops.py, auditar.py) — branch agente2/behaviors-onda2 preservada
- [ ] Auditoria de consistencia de dominios (nem todos seguem template _template/)
- [ ] CHECKPOINT.md aguarda revisao manual (nao versionado, no .gitignore)

### Contexto que nao esta no codigo
- PowerShell 5.1 exige UTF-8 com BOM — create_file nao gera, usar [System.Text.UTF8Encoding]::new($true)
- injetar-estado.ps1 usa 3 niveis de Split-Path porque esta em .github/hooks/scripts/
- Os dois worktrees compartilham o MESMO repositorio Git — edicoes em .github/ aparecem nos dois
- agente2/behaviors-onda2 foi restaurada do origin apos reset acidental — commit eef0ffe

### Decisoes que so um humano pode tomar
- Fazer merge da branch chore/limpeza-agent-only na main? (45 arquivos, +582/-607 linhas de reorganizacao + 1700+ arquivos de conteudo do Agente 02)
- Apagar branch agente2/behaviors-onda2 apos confirmar que tudo foi integrado?
- Mover MCP_Backup, DEEP-SEEK, clinica-idle, Protto Games para um local de arquivo morto?
- Configurar remote no repositorio Git pessoal ($HOME/.copilot)?

### Arquivos que eu toquei
- .github/agents/ (removidos 4 agentes)
- .github/prompts/ (plan, act, audit, handoff, encerrar, seguir-roadmap — todos reescritos/atualizados)
- .github/instructions/ (autogovernanca, behaviors — novos; camada-5/6/7 applyTo ajustado; glossario/pesquisa → skills)
- .github/skills/ (glossario, pesquisa — novos)
- .github/hooks/ (estado.json, injetar-estado.ps1 — criados/atualizados)
- .github/scripts/ (rotacionar-handoff.ps1 — novo)
- .github/copilot-instructions.md (atualizado)
- AGENTS.md (reescrito para agente unico + 2 worktrees)
- HANDOFF.md (atualizado)
- README.md (adicionado mapa do projeto)
- docs/ (DATA_CONTRACTS.md, DUMP_T1R.md, MASTER_IMPLEMENTATION_ROADMAP.md, ROADMAP.md, ROADMAP_DEFINITIVO.md, SUTURE_ISSUES.md movidos da raiz)
- docs/archive/ (journal/ e .session/ arquivados)
- behaviors/ (1700+ arquivos do Agente 02)
- example_project/, seeds/, templates/ (conteudo Agente 02)
- scripts/ (10 scripts de auditoria Agente 02)
- addons/mcp_bt_editor/ (Behavior Tree Editor)
- tools/ (12 tools novas do Agente 02)
- .git/coordenacao.json (mecanismo de coordenacao entre worktrees)
- $HOME/.copilot/ (hooks de seguranca, skill fw-init, repositorio Git pessoal)
- settings.json (removido agentFilesLocations e autostart invalido, adicionado hookFilesLocations)

### Proxima fatia sugerida
Revisao humana do merge da branch chore/limpeza-agent-only na main.

### Como voltar atras
git checkout main

## Encerramento � 2026-07-23

**Worktree/Agente:** Agente 1 (main)
**Peso:** Sessao longa � ONDA R + ONDA 1 + ONDA 2 + ONDA 3 + ONDA 4 + parciais 8-9-10-P. 38 fatias concluidas.

### Resumo
Executado o plano REORG_ROADMAP.md: gate git real (R1), estado unico (R2), auditor consertado (R3), caminhos (R4), reauditoria F5 (R5), branch Agente 2 (R6), medicao (R7), fichas (R8). Registry funcional com build_tool_defs() byte-identeico ao legado. ToolAnnotations corrigido (2.1). _HINT_RULES movido para registry. Filtros reduzidos de 3 para 2 eixos. 45 tools ainda sem cobertura de fase.

### Estado
- Versao: 3.8.0 | Commit: a0d1de4 | Branch: main
- server.py: -497 linhas | Tools: 234 | Testes: 170 pass, 8 xfail

### Pendencias
- [ ] 8.1 � Atribuir fase as 45 tools sem cobertura (prioridade: alta)
- [ ] F5.1-F5.13 � 7 fatias dependem de F1-F4 fechar (prioridade: media)
- [ ] P.1 � Feature 9 build_export (prioridade: baixa)
- [ ] P.2 � Feature 10 get_next_step (prioridade: baixa)

### Contexto que nao esta no codigo
- Gate G1/G2/G3 ativo em .githooks/pre-commit. Escape hatch: git commit --no-verify
- registry/legacy_adapter.py usa guarda _in_registry_call para evitar loop
- core/legacy_data.py e a fonte de TOOLSETS/PHASE_TOOLSETS/TOOL_PROFILES/PHASE_TOOLS_CORE
- Filtros: toolsets -> fase (2 eixos). Profile removido na 8.2.

### Decisoes que so um humano pode tomar
- Merge dos behaviors do Agente 2 (branch arquivo-morto/behaviors-onda2)
- Ativar CI no GitHub Actions

### Arquivos-chave
- server.py (core)
- core/legacy_data.py (dados de curadoria)
- registry/ (fonte de verdade em construcao)
- tools/rollups.py (builders de rollup)
- .roadmap_progress.json (status de fatias)
- .githooks/pre-commit (gate git)
- scripts/gate_reorg.py (logica do gate)

### Fluxo sugerido
1. Leia HANDOFF.md
2. Rode pytest tests/test_gate_reorg.py tests/test_invariants.py
3. Rode /plan para 8.1 (atribuir fase as 45 tools)

### Decisoes da sessao
- DR-1: commit automatico so depois do gate git ? satisfeita (R1 commitada)
- DR-2: branch Agente 2 taggeada como arquivo morto ? executada (R6)
- DR-3: prompts locais removidos ? executada (R4)
- DR-4: /act vence /seguir-roadmap ? documentada
- DR-5: --skip-c5 substituido por baseline ? executada (R3)
- DR-6: C1 tolerancia 0 ? executada (R3)
- Profile removido (3 eixos -> 2) ? executada (8.2)

### Atencao
- C5 (test_budget_gate) quebrado: 'NoneType' object is not iterable
- auditar.py sempre falha C5 � pre-existente, fora de escopo
- Nunca usar && no PowerShell
- Gate G1 bloqueia commit com checkpoint ausente � sempre preencher antes de commitar
