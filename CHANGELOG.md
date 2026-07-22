# CHANGELOG — MCP Godot Agent

## v3.2.1 (2026-07-22) — Editor Visual + ONDA 2~4 (AGENTE 02)

### Editor Visual de Behavior Trees (FATIA 2.AV)
- addons/mcp_bt_editor/ — 10 arquivos, ~2.620 linhas GDScript
- 16 features: dock, paleta 249 behaviors, drag-drop, 4 portas coloridas,
  validacao DAG, reroute, expression, auto-arrange, undo/redo, preview WS 9082,
  GraphFrame, minimap, breakpoints, watch window
- Integrado com discover_behaviors, mcp_dock, .tres, behavior.json

### AssetLib Prep + Style Kit + Seguranca (FATIAS 2.AW, 2.AL, 2.AM)
- addons/mcp_addon/: plugin.cfg completo, README PT/EN, LICENSE, CHANGELOG
- tools/style_kit.py (290 linhas): 4 presets de estilo visual
- tools/asset_security.py (280 linhas): 7 verificacoes, 8 padroes suspeitos

### Jogos-Exemplo + Templates (FATIAS 2.AX)
- example_project/: platformer (15b), rpg (20b), puzzle (10b), shooter (14b)
- templates/: 5 generos (shooter, idle, visual novel, roguelike, tower defense)
- seeds/: +1 survivors_like (total 4 seeds)

### Infraestrutura (FATIAS 2.AE, 2.AF, 2.AK, 2.AS, 2.AQ, 2.AR, 2.AT)
- RAG local, Entity Index, Fix Recipes (7 receitas), Reproducibility Seed
- Context Compaction, Model Routing, Undo Unify — registrados no server.py
- +16 tools registradas sem reorganizar grupos

### Qualidade Enterprise
- Score 7/7: 249/249 @tool, warnings, behavior.json, CHANGELOG, README, testes
- 189/189 .tres para behaviors com parametros
- runtime_bridge_client.gd (151 linhas) criado
- docs/: +5 arquivos (getting-started, tools, guia-migracao, modo-professor, guia-publicacao)

### ONDA 3+4 — Preparacao
- tests/playtest_personas.json: 5 personas de playtest
- docs/modo-professor.md: template didatico com exemplos
- scripts/adversarial_review.py: revisor standalone (230 linhas)
- .github/FUNDING.yml, BRAND.md, DISCUSSION_TEMPLATES/
- ONDA 4 terreno preparado (nada publicado)

### Scripts
- scripts/project_health.py: dashboard de saude
- scripts/behavior_deps.py: grafo de dependencias
- scripts/fix_behavior_quality.py: fixer com --dry-run
- scripts/adversarial_review.py: revisor adversarial
- 9 scripts de manutencao no total

### Auditorias
- 3 auditorias completas: 25 bugs encontrados -> 25 corrigidos
- validate_gdscript.py: todos PASS
- 14 commits na sessao

## v4.0.0 (2026-07-21) — Arsenal Completo de Behaviors (AGENTE 02)

### Behaviors: 118 → 249 (+131)
- Catalogo completo implementado: 249 behaviors para Godot 4.7
- Todos os 20+ grupos fechados (PERSONAGEM, GENEROS, SISTEMA, ESTRUTURA, CAMERA, SOCIAL, CINEMATICA, INIMIGO/AI, SHADERS, MULTIPLAYER, ACESSIBILIDADE, LOCALIZACAO, INPUT AVANCADO, SAVE AVANCADO, PCG, OBSERVABILIDADE, MODDING, PLUGIN SYSTEM, LIFECYCLE, PERFORMANCE, ANIMACAO, TILEMAP)
- ~14.000 linhas de GDScript total

### Qualidade
- 84 behavior.json reconstruidos (JSON invalido corrigido)
- 34 sinais nao emitidos corrigidos
- 0 @tool missing, 0 _get_configuration_warnings missing
- 0 class_name conflicts, 0 _initialized missing
- validate_gdscript: ALL PASS em 249 behaviors
- Script `scripts/audit_behaviors.py` criado para auditoria automatica

### Infraestrutura
- `.roadmap_progress_a2.json` reconstruido com precisao (249 entradas)
- `HANDOFF.md` atualizado com resumo completo

## v3.5.0 (2026-07-19) — Sessao de Polimento + Camada 5 Gameplay (AGENTE 02)

### Polimento (F1-F7)
- **F1 — Diagnostico:** 51% coverage, 18 tools sem teste
- **F2 — Cobertura Tier-1:** +18 handlers sinteticos, 87.8% → 100% coverage (0 tools sem cobertura)
- **F3 — Regressao Visual:** `manage_visual_baselines()`, threshold calibrado, `--visual` no `auditar.py`
- **F4 — Perf Regression:** Handler sintetico para `perf_regression_track`
- **F5 — Canary Queries:** 14 → 48 queries, 45 tools cobertas
- **F6 — Audio Engine:** `tools/audio_ops.py` (fachada unificada), play/set/stop no runtime bridge GDScript
- **F7 — Documentacao:** HANDOFF, NEXT_STEP, roadmap atualizados

### Camada 5 — Gameplay (8 fatias, 28 funcoes)
- **5.1 — Conquistas + Cloud Save:** `tools/achievement_ops.py` (3 funcoes)
- **5.2 — Suporte a Mods:** `tools/mod_ops.py` (2 funcoes)
- **5.3 — Cutscene/Cinematica:** `tools/cutscene_ops.py` (3 funcoes)
- **5.4 — Telemetria + Replay:** `tools/telemetry_ops.py` (4 funcoes)
- **5.5 — Dificuldade + Quest + Balance:** `tools/adaptive_ops.py` (3 funcoes)
- **5.6 — Acessibilidade:** `tools/accessibility_ops.py` (5 funcoes)
- **5.7 — Trailer + Onboarding:** `tools/trailer_ops.py` + `tools/onboarding_ops.py` (6 funcoes)
- **5.8 — Dialogo NPC:** `tools/dialogue_ops.py` expandido (2 funcoes)

### Auditorias (3 ciclos)
- 5 CRITICAL corrigidos (C1: _json→json, C2-C5: GDScript audio)
- 4 HIGH corrigidos (H1: 5 tools faltantes, H2-H4: validacoes)
- 5 gaps fechados (G1-G5: semver, level_range, count, imports)

## v3.4.0 (2026-07-19) — Camada 4: Extensoes de Processo (AGENTE 02)

### B2 — CI Verificação
- `.github/workflows/verification.yml` — pipeline com 7 jobs (budget, snapshot, governor, syntax, regressão, audit, summary)
- Permissions com menor privilégio, concurrency, timeout-minutes, cache pip

### B3 — gdtoolkit Gate
- `tools/code_quality_ops.py` — gdlint 4.5.0 + gdformat + gdradon integrados como gate no `run_verification_pipeline`
- `.gdlintrc` — configuração YAML com limiares (80 linhas/função, CC≤10, god_class detection)
- `requirements.txt` — `gdtoolkit>=4.0,<5.0`
- 19/19 testes automatizados

### B4 — Análises Específicas (9 ops)
- `find_unused_functions`, `detect_gdscript_antipatterns`, `find_orphan_signals_nodes`, `check_naming_convention`
- `find_duplicate_code_blocks`, `detect_scene_reference_cycles`, `check_import_settings_consistency`
- `semantic_code_search`, `suggest_refactor`

### B5 — Segurança Supply-Chain
- `tools/security_ops.py` — `scan_addon_vulnerabilities` (12 padrões), `check_addon_license` (19 tipos, regex)
- 15 edge case + 25 license accuracy tests

### B6 — agent_manage
- `tools/agent_ops.py` — 8 funções: file lock, task queue, peer review, compare outputs, context pack, onboarding

### B7 — Save Schema + Migração
- `tools/gamestate_ops.py` — `generate_save_schema`, `migrate_save` (rename, add, remove, transform)

### B8 — Dead-End Detection
- `tools/dialogue_ops.py` — `find_dialogue_dead_ends` (DFS, ciclos), `validate_quest_completion`

### B9 — Documentação Automática
- `tools/doc_ops.py` — `generate_changelog`, `generate_project_readme`, `generate_project_wiki`

---

## v3.3.1 (2026-07-14) — Blocos 1-3 + Smoke Test

### Bloco 1 — Auditoria de Wiring (3 ferramentas)
- `audit_input_map` — ações declaradas vs usadas no código
- `audit_autoloads` — singletons registrados vs referenciados
- `audit_scene_reachability` — BFS de cenas a partir da raiz, detecta change_scene_to_file

### Bloco 2 — UID + Save (2 ferramentas)
- `audit_uid_consistency` — UID declarado vs .uid file, duplicados, uid_cache.bin
- `audit_save_compatibility` — chaves escrita/leitura, versionamento, migração

### Bloco 3 — Documentação
- `FEATURES.md` — registro de wiring do Shardbreaker com dados reais das 5 auditorias
- `AUDIT_PROTOCOL.md` — cadência, escopo, regras de deleção segura

### Integração de Automação (6 pontos de disparo)
- `git_commit_checkpoint` → wiring + UID warnings (não bloqueia)
- `run_verification_pipeline` → etapa 5: audit_scene_reachability
- `hook_stop.py` → audit_scene_reachability no encerramento
- `analyze_game_structure` → campo wiring_status agregado
- `suggest_next_steps` → sugestão priority 0 com resumo de issues
- `regression_test` → 10 cenários (REGRESS-01 a REGRESS-10)

### Smoke Test — Hooks do VS Code
- ❌ NO-GO: agent hooks (PreToolUse/PostToolUse/Stop/SessionStart) não disparam com `vizards.deepseek-v4-for-copilot` v0.6.2
- Causa: a extensão implementa loop de tool-calling próprio, bypassando hooks nativos
- Consequência: gates residem nos handlers MCP (safety.py, hook_stop.py), não em hooks VS Code
- BYOK nativo testado sem sucesso para hooks

### Métricas
- **211 tools**, **76 módulos**, **5 ferramentas de auditoria**, **10 cenários de regressão**
- **3 blocos entregues**, **6 integrações de automação**

---

## v3.3.0 (2026-07-12) — Onda 0.1 completa

### Features Fase 1 (9 + Task B)
- Feature 4-9 + Task B já documentados

### Features Grupo C (4)
- **C1**: `find_unused_resources` — detecção de assets órfãos (matching exato, não substring; autoloads como referência implícita)
- **C2**: `analyze_signal_flow` — conexões de sinal órfãs (método renomeado/removido)
- **C3**: `set_auto_dismiss` — fechamento automático de diálogos modais (GDScript + Python)
- **C4**: `fuzzy_suggest` — sugestão por proximidade generalizada, aplicado em get_node_property + list_signals

### Feature 10
- `run_stress_test` — orquestra game_spawn_node + inject_input_event + game_performance + capture_runtime_errors

### Shader Editor (A1)
- `read_shader`, `edit_shader` (validação via RenderingServer), `get_shader_params` (parse de uniforms)

### Bugs corrigidos (Onda 0.1)
- PHASE_TOOLSETS não filtrava projetos limpos — `_get_phase_tools()` auto-cria `.mcp_phase_state.json`
- `PhaseState.load()` não persistia estado inicial no disco
- Validação de gênero case-sensitive em `project_brief_ops` e `balance_ops`
- BUG-008: dead imports em find_unused_resources.py
- BUG-009: str/Path em milestone_ops.py

### Métricas
- **191 tools**, **72 módulos**, **22 patches**, **10 features Fase 1**, **4 Grupo C**, **6 fases**
- **55+ bugs corrigidos**, **18 regras LEARNINGS (R1-R18)**

---

## v3.2.1 (2026-07-12) — Sessão de auditoria, hardening + Item 1+2 do plano de evolução

### Feature 4: Vibe Coding Mode fallback
- 8 funções em `scene_ops.py` com fallback para modo vibe (load_scene_tree, add_node, delete_node, set/get_node_property, reparent_node, instance_scene_as_child, connect_signal)
- `vibe_ops.py` reescrito com `_load_vibe_state`/`_save_vibe_state` (`.mcp_vibe_state.json`)
- `config_lock.py`: CONFIG_FILE_LOCK, VIBE_STATE_LOCK, BRIEF_STATE_LOCK (threading.Lock)
- `create_scene` auto-configura `run/main_scene`

### Feature 5: Project Brief
- `project_brief_ops.py`: set/get/update_project_brief com `_validate_genre()` e VALID_PLATFORMS
- `orchestrator.py`: fallback para `get_project_brief()` quando `art_style=None`

### Feature 6: Batch Entity Creation
- `orchestrator.py`: `create_entities(entities, stop_on_first_failure)` com MAX_BATCH_SIZE=20
- Counter-based duplicate detection, execução sequencial

### Feature 7: Hook Stop
- `hook_stop.py`: lê JSON com guard `stop_hook_active`, verifica `.mcp_gate_failed`
- `safety.py`: `_write_gate_failed_marker`/`_clear_gate_failed_marker` usam `_get_active_project()`
- `script_ops.py`: `_validate_after_edit` limpa marker em sucesso

### Task B: tool_catalog — scoring PT→EN
- BM25 substituído por scoring ponderado: nome +3pts, ops +2pts, descrição/params +1pt, rollup bônus +1pt
- 35 aliases PT→EN + `QUERY_ALIASES_ACCENT_ONLY` ("nó"→"node" só com acento)
- Filtro e scoring usam token matching exato (não substring)
- `rank-bm25` removido do código e do venv

### Feature 8: Toolsets por Fase (PHASE_TOOLSETS)
- 6 fases cumulativas: IDEIA(28)→DESIGN(+28)→PROTOTIPO(+48)→CONTEUDO(+35)→POLIMENTO(+27)→PRONTO_PARA_LANCAR(+25) = 191
- Filtro dinâmico em `_tool_defs()` (lê `.mcp_phase_state.json` do disco)
- Cache invalidado via callback registration (`set_cache_invalidator`, sem import circular)
- Visibilidade apenas — `_build_handlers()` NÃO é filtrado
- `safety_manage` disponível desde IDEIA
- Fix: `Path()` wrapper em `PhaseState._get_file_path()`

### Bugs corrigidos (sessão)
- `_find_node_in_parsed`: parent="." (Godot root children)
- `_snapshot_scene`: path relativo → absoluto
- `_connect_signal_file`: kwargs from_node_path/to_node_path
- Godot PID 22104 stuck (morto)
- 39 temp projects sem `run/main_scene` (auto-config)
- Race condition: `_load_brief_state()` sem lock
- Race condition: `_validate_after_edit` nunca limpava gate marker
- `_get_file_path()`: string vs Path (`Path()` wrapper adicionado)

### Métricas
- **191 tools**, **69 módulos**, **18 patches**, **8 features da Fase 1**, **6 fases**
- **55+ bugs corrigidos** em 12 rodadas de auditoria

---

## v3.2.1 (2026-07-12) — Sessão de auditoria, hardening + Item 1+2 do plano de evolução

### Item 1: Pipeline de Verificação (run_verification_pipeline)
- **Nova tool:** `run_verification_pipeline` — pipeline completo em 4 etapas (compile → headless run → screenshot → GUT)
- **Módulo novo:** `tools/verification_ops.py` (330 linhas)
- **Relatório JSON consolidado** com status de cada etapa, early exit na primeira falha
- **Screenshot via `--write-movie`** com SW_HIDE (não usa `--headless` — evita crash SIGSEGV do renderer DUMMY)
- **Tratamento de ambiguidade:** retorna `ambiguous` se `test_scene` não definido
- **6 bugs encontrados e corrigidos** (BUG-V01 a V06): variáveis mortas, self-assignment, mutação de dict, partial output em timeout

### Item 2: Fluxo EARS + Pipeline (Padrão de Fechamento de Pendência)
- **AGENTS.md** criado no Star Colony com regra de comportamento obrigatória
- Fluxo documentado: receber → EARS → aprovar → implementar → pipeline → relatório → fechar condicional
- **EARS-B implementado:** VFX de evolução visual L1→L2→L3 com gatilho provisório (tecla U)
- **_draw() modificado:** escala por nível (L1=1.0, L2=1.15, L3=1.30) + borda (L2=prata, L3=douro)
- **VFX:** `spawn_explosion`, `spawn_floating_text`, `add_shake(0.15, 3.0)` via `vfx_system.gd`
- **Teste visual:** pixel analysis confirma bordas prateada/dourada exclusivas por nível

### Documentação
- **MCP_ESTADO_ATUAL.md** sincronizado com 191 tools, 69 módulos, v3.2.1
- **pendencias.md** criado (bugs ativos + resolvidos)
- **decisoes.md** (Star Colony) atualizado com EARS-B

### Métricas atualizadas
- **191 tools** (+2: run_verification_pipeline + 1 rollup), **69 módulos** (+5)
- **49 bugs corrigidos** (+6 BUG-V01~V06) em 12 rodadas de auditoria

### Correções de segurança
- **Sandbox conectado à escrita:** `write_file` e `safe_write_gdscript` agora chamam `validate_gdscript_code()` antes de escrever .gd em disco (36/36 padrões bloqueados com confirmação de disco)
- **Normalização de código:** `_normalize_gdscript()` remove comentários, colapsa whitespace, resolve concatenação literal — fecha 3/4 bypasses (comentário, quebra de linha, concatenação)
- **Escopo documentado:** aviso no topo de `gdscript_sandbox.py` — é filtro de texto, não sandbox de execução isolada
- **`safe_write_gdscript` corrigido:** path relativo ao projeto, `godot_console_path` para `--headless`, timeout handler com `skipped: True` explícito
- **Godot check desligado por padrão:** flag `tentar_checagem_godot` (default false) — R12 confirmado em 3 tipos de projeto (minimal, Star Colony, completo)

### Correções de bugs
- **B1 documentado:** `_parse_tscn_node_refs` regex `\d+` não detecta IDs alfanuméricos (ex: `1_sh`)
- **B2 corrigido:** `run_scripted_tests` agora suporta runtime tools (`godot_screenshot`, `godot_runtime_info`)
- **B3 corrigido:** `dump_mcp_state` retorna `"status": "success"` no nível raiz
- **Handler órfão:** adicionado schema `estimate_tool_tokens` em `_tool_defs()` (estava só no handler)
- **PATCH 12 auditado:** `_cmd_custom` com validação de callable, `_reply` com verificação de erro

### Infraestrutura
- **Hook Stop NUCLEO:** `check-gate-failed.ps1` — bloqueia encerramento se `.mcp_gate_failed` existir
- **pre-commit versionado:** movido para `.github/hooks/scripts/pre-commit.ps1`
- **Limpeza:** removidos MCPs duplicados (`sistema/mcp-godot/`, `refinamento-mcp/`)
- **config.json untracked:** removido do Git para evitar reversões acidentais

### Documentação
- **Todos os docs atualizados para v3.2:** README, ARQUITETURA_MCP, GUIA_CONEXAO, GUIA_INSTALACAO, LEARNINGS
- **LEARNINGS.md R12 ampliado:** cobre `--headless --script` E `--check-only`
- **MCP ESTADO ATUAL:** documento externo sincronizado com 190 tools, 64 módulos, 18 patches

**Total:** 190 ferramentas, 190 handlers, 64 módulos, 18 patches, 5 grupos de auditoria

## v3.2.0 (2026-07-12) — Sessão anterior
- **PATCH 14:** Testes roteirizados — smoke_test, regression_test, run_scripted_tests, dump_mcp_state, estimate_tool_tokens
- **PATCH 15:** Validação de referências — validate_project_refs, find_usages (estático, offline)
- **PATCH 16:** Asset manifest — import_asset_manifest (5 fontes), create_asset_manifest
- **GRUPO 1:** Validação GDScript no write_file + safe_write R9 deep validation
- **GRUPO 2:** git_commit_checkpoint com gates de compilação + GUT skipped
- **GRUPO 3:** --profile (core/dev/full) + MCP_TOOL_PROFILE + estimate_tool_tokens
- **GRUPO 4:** config.local.json + GODOT_MCP_* env vars (confirmado)
- **GRUPO 5:** allow_paid_generation=False + estimated_cost
- **Total:** 189 ferramentas, 64 módulos, 43 bugs corrigidos em 10 rodadas de auditoria

## v3.1.0 (2026-07-12)
- **PATCH 12:** Runtime Bridge — servidor TCP GDScript (8790) + cliente Python + 4 tools (screenshot, runtime_info, custom_command, list_custom_commands)
- **PATCH 12.1:** Process Lifecycle — godot_run_project, godot_stop_project, godot_wait_for_bridge com save-before-kill e proteção contra PID reaproveitado
- **PATCH 13:** ClassDB introspecção — godot_class_ref via extension_api.json (Python puro), 1074 classes com herança, fuzzy suggestions
- **PATCH 17:** Curadoria de toolset — `--toolsets` com 10 grupos nomeados
- **PATCH 18:** Marcador `.mcp_gate_failed` integrado com hooks

## v3.0.1 (2026-07-10)
- Orquestrador Genius: Saga + Circuit Breaker + Decision Engine + Reconciliation
- 172 ferramentas no total
- Estrutura `addons/` corrigida, bridges restaurados

## v3.0 (2026-07-10)
- Pipeline Executor: `create_entity`, `project_status`
- Decision Engine: decide automaticamente arte placeholder vs FLUX
- 171 ferramentas no total
- 46 bugs corrigidos (grupos CRITICAL, HIGH, MEDIUM, LOW)
- Servidor completo e autocontido

## v2.9 (2026-07-09)
- Repositório completo e autocontido
- 143+ ferramentas
- MCP bridge + Game bridge addons incluídos
